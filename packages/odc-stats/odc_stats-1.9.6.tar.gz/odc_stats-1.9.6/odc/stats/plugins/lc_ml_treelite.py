"""
Base class for treelite models in LandCover PipeLine
"""

from abc import abstractmethod
from collections.abc import Sequence

import os
import sys
import numpy as np
import numexpr as ne
import xarray as xr
import dask.array as da
from dask.distributed import get_worker

from datacube.model import Dataset
from odc.geo.geobox import GeoBox
from odc.algo._memsink import yxbt_sink, yxt_sink
from odc.stats.io import load_with_native_transform

from odc.algo import expr_eval
from odc.stats.model import DateTimeRange
from ._registry import StatsPluginInterface
from ._worker import TreeliteModelPlugin
import tl2cgen
import logging


def mask_and_predict(
    block, block_info=None, ptype="categorical", nodata=np.nan, output_dtype="float32"
):
    worker = get_worker()
    plugin_instance = worker.plugin_instance
    predictor = plugin_instance.get_predictor()

    block_flat = block.reshape(-1, block.shape[-1])
    # mask nodata and non-veg
    mask_flat = ne.evaluate(
        "where((a==a)&(b>0), 1, 0)",
        local_dict={"a": block_flat[:, 0], "b": block_flat[:, -1]},
    ).astype("bool")
    block_masked = block_flat[mask_flat, :-1]

    prediction = np.full(
        (block.shape[0] * block.shape[1], 1), nodata, dtype=output_dtype
    )
    if block_masked.shape[0] > 0:
        dmat = tl2cgen.DMatrix(block_masked)
        output_data = predictor.predict(dmat).squeeze(axis=1)
        # round the number to float32 resolution
        output_data = np.round(output_data, 6)
        if ptype == "categorical":
            prediction[mask_flat] = output_data.argmax(axis=-1)[..., np.newaxis]
        else:
            prediction[mask_flat] = output_data
    return prediction.reshape(*block.shape[:-1])


class StatsMLTree(StatsPluginInterface):
    NAME = "ga_ls_ml_tree"
    SHORT_NAME = NAME
    VERSION = "0.0.1"
    PRODUCT_FAMILY = "lccs"

    def __init__(
        self,
        output_classes: dict,
        model_path: str,
        mask_bands: dict | None = None,
        temporal_coverage: dict | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"{self.model_path} not found")
        self.dask_worker_plugin = TreeliteModelPlugin(model_path)
        self.output_classes = output_classes
        self.mask_bands = mask_bands
        self.temporal_coverage = (
            temporal_coverage if temporal_coverage is not None else {}
        )
        self._log = logging.getLogger(__name__)

    def input_data(
        self, datasets: Sequence[Dataset], geobox: GeoBox, **kwargs
    ) -> xr.Dataset:
        # load data in the same time and location but different sensors
        data_vars = {}

        for ds in datasets:
            if "gm" in ds.type.name:
                input_bands = self.input_bands[:-1]
            else:
                input_bands = self.input_bands[-1:]

            xx = load_with_native_transform(
                [ds],
                bands=input_bands,
                geobox=geobox,
                native_transform=self.native_transform,
                basis=self.basis,
                groupby=None,
                fuser=None,
                resampling=self.resampling,
                chunks={"y": -1, "x": -1},
                optional_bands=self.optional_bands,
                **kwargs,
            )
            if "gm" in ds.type.name:
                input_array = yxbt_sink(
                    xx,
                    (self.chunks["x"], self.chunks["y"], -1, -1),
                    dtype="float32",
                    name=ds.type.name + "_yxbt",
                ).squeeze("spec")
                data_vars[ds.type.name] = input_array
            else:
                for var in xx.data_vars:
                    data_vars[var] = yxt_sink(
                        xx[var].astype("uint8"),
                        (self.chunks["x"], self.chunks["y"], -1),
                        name=ds.type.name + "_yxt",
                    ).squeeze("spec")

        coords = {dim: input_array.coords[dim] for dim in input_array.dims}
        return xr.Dataset(data_vars=data_vars, coords=coords)

    def impute_missing_values(self, xx: xr.Dataset, image):
        imputed = None
        for var in xx.data_vars:
            if var in self.mask_bands:
                continue
            nodata = xx[var].attrs.get("nodata", -999)
            imputed = expr_eval(
                "where((a==a)|(b<=nodata)|(b!=b), a, b)",
                {
                    "a": image,
                    "b": xx[var].data,
                },
                name="impute_missing",
                dtype="float32",
                **{"nodata": nodata},
            )
        return imputed if imputed is not None else image

    def preprocess_predict_input(self, xx: xr.Dataset):
        images = []
        veg_mask = None

        def convert_dtype(var):
            nodata = xx[var].attrs.get("nodata", -999)
            image = expr_eval(
                "where((a<=nodata), _nan, a)",
                {
                    "a": xx[var].data,
                },
                name="convert_dtype",
                dtype="float32",
                **{"nodata": nodata, "_nan": np.nan},
            )
            return image

        for var in xx.data_vars:
            if var not in self.mask_bands:
                # filter and impute by sensors
                if self.temporal_coverage.get(var) is not None:
                    temporal_range = [
                        DateTimeRange(v) for v in self.temporal_coverage.get(var)
                    ]
                    for tr in temporal_range:
                        if xx.solar_day.data.astype("M8[ms]") in tr:
                            self._log.info("Impute missing values of %s", var)
                            image = convert_dtype(var)
                            images += [
                                self.impute_missing_values(xx.drop_vars(var), image)
                            ]
                            break
                else:
                    # use data from all sensors
                    image = convert_dtype(var)
                    images += [image]
            else:
                veg_mask = expr_eval(
                    "where(a==_v, 1, 0)",
                    {"a": xx[var].data},
                    name="make_mask",
                    dtype="float32",
                    **{"_v": int(self.mask_bands[var])},
                )

        if veg_mask is None:
            raise TypeError("Missing Veg Mask")

        images = [
            da.concatenate([image, veg_mask[..., np.newaxis]], axis=-1).rechunk(
                (None, None, image.shape[-1] + veg_mask.shape[-1])
            )
            for image in images
        ]
        return images

    @abstractmethod
    def predict(self, input_array):
        pass

    @abstractmethod
    def aggregate_results_from_group(self, predict_output):
        pass

    def reduce(self, xx: xr.Dataset) -> xr.Dataset:
        try:
            images = self.preprocess_predict_input(xx)
        except TypeError as e:
            self._log.warning(e)
            sys.exit(0)

        res = []

        for image in images:
            res += [self.predict(image)]

        res = self.aggregate_results_from_group(res)
        attrs = xx.attrs.copy()
        dims = list(xx.sizes.keys())[:2]
        data_vars = {"predict_output": xr.DataArray(res, dims=dims, attrs=attrs)}
        coords = {dim: xx.coords[dim] for dim in dims}
        return xr.Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
