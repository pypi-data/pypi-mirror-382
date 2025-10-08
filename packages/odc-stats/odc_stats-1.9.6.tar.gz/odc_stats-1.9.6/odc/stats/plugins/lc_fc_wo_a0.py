"""
Plugin of Module A0 in LandCover PipeLine
"""

from functools import partial
from collections.abc import Iterable

import numpy as np
import xarray as xr
import dask.array as da
from odc.algo import keep_good_only
from odc.algo._masking import (
    _fuse_mean_np,
    _xr_fuse,
    mask_cleanup,
    to_float,
    _nodata_fuser,
)
from odc.stats._algebra import median_ds
from odc.algo import expr_eval

from ._registry import StatsPluginInterface, register

NODATA = 255


class StatsVegCount(StatsPluginInterface):
    NAME = "ga_ls_lccs_fc_wo_a0"
    SHORT_NAME = NAME
    VERSION = "0.0.1"
    PRODUCT_FAMILY = "lccs"

    BAD_BITS_MASK = {"cloud": (1 << 6), "cloud_shadow": (1 << 5)}

    def __init__(
        self,
        ue_threshold: int | None = None,
        veg_threshold: int | None = None,
        cloud_filters: dict[str, Iterable[tuple[str, int]]] = None,
        **kwargs,
    ):
        super().__init__(input_bands=["water", "pv", "bs", "npv", "ue"], **kwargs)

        self.ue_threshold = ue_threshold if ue_threshold is not None else 30
        self.veg_threshold = veg_threshold if veg_threshold is not None else 2
        self.cloud_filters = cloud_filters if cloud_filters is not None else {}

    def native_transform(self, xx):
        """
        Loads data in its native projection. It performs the following:

        1. Load all fc and WO bands
        3. Set all pixels that are not clear and dry to NODATA
        4. Calculate the clear wet pixels
        5. Drop the WOfS band
        """

        # valid and dry pixels not mask against bit 4: terrain high slope,
        # bit 3: terrain shadow, and
        # bit 2: low solar angle
        valid = (xx["water"].data & ~((1 << 4) | (1 << 3) | (1 << 2))) == 0

        # clear wet pixels not mask against bit 2: low solar angle
        wet = (xx["water"].data & ~(1 << 2)) == 128

        # clear dry pixels
        clear = xx["water"].data == 0

        # dilate both 'valid' and 'water'
        for key, val in self.BAD_BITS_MASK.items():
            if self.cloud_filters.get(key) is not None:
                raw_mask = (xx["water"] & val) > 0
                raw_mask = mask_cleanup(
                    raw_mask, mask_filters=self.cloud_filters.get(key)
                )
                valid = expr_eval(
                    "where(b>0, 0, a)",
                    {"a": valid, "b": raw_mask.data},
                    name="get_valid_pixels",
                    dtype="bool",
                )
                clear = expr_eval(
                    "where(b>0, 0, a)",
                    {"a": clear, "b": raw_mask.data},
                    name="get_clear_pixels",
                    dtype="bool",
                )
                wet = expr_eval(
                    "where(b>0, 0, a)",
                    {"a": wet, "b": raw_mask.data},
                    name="get_wet_pixels",
                    dtype="bool",
                )

        xx = xx.drop_vars(["water"])

        # get "clear" wo pixels, both dry and wet used in water_frequency
        wet_clear = expr_eval(
            "where(a|b, a, _nan)",
            {"a": wet, "b": clear},
            name="get_clear_pixels",
            dtype="float32",
            **{"_nan": np.nan},
        )

        # get "valid" wo pixels, both dry and wet
        # to remark nodata reason in veg_frequency
        wet_valid = expr_eval(
            "where(a|b, a, _nan)",
            {"a": wet, "b": valid},
            name="get_valid_pixels",
            dtype="float32",
            **{"_nan": np.nan},
        )

        # Pick out the fc pixels that have an unmixing error of less than the threshold
        valid = expr_eval(
            "where(b<_v, a, 0)",
            {"a": valid, "b": xx["ue"].data},
            name="get_low_ue",
            dtype="bool",
            **{"_v": self.ue_threshold},
        )
        xx = xx.drop_vars(["ue"])
        valid = xr.DataArray(valid, dims=xx["pv"].dims, coords=xx["pv"].coords)

        xx = keep_good_only(xx, valid, nodata=NODATA)
        xx = to_float(xx, dtype="float32")

        xx["wet_clear"] = xr.DataArray(
            wet_clear, dims=xx["pv"].dims, coords=xx["pv"].coords
        )
        xx["wet_valid"] = xr.DataArray(
            wet_valid, dims=xx["pv"].dims, coords=xx["pv"].coords
        )

        return xx

    def fuser(self, xx):
        wet_clear = xx["wet_clear"]
        wet_valid = xx["wet_valid"]

        xx = _xr_fuse(
            xx.drop_vars(["wet_clear"]),
            partial(_fuse_mean_np, nodata=np.nan),
            "",
        )

        xx["wet_clear"] = _nodata_fuser(wet_clear, nodata=np.nan)
        xx["wet_valid"] = _nodata_fuser(wet_valid, nodata=np.nan)

        return xx

    def _veg_or_not(self, xx: xr.Dataset):
        # either pv or npv > bs: 1
        # otherwise 0
        data = expr_eval(
            "where((a>b)|(c>b), 1, 0)",
            {"a": xx["pv"].data, "c": xx["npv"].data, "b": xx["bs"].data},
            name="get_veg",
            dtype="uint8",
        )

        # mark nans
        data = expr_eval(
            "where(a!=a, nodata, b)",
            {"a": xx["pv"].data, "b": data},
            name="get_veg",
            dtype="uint8",
            **{"nodata": int(NODATA)},
        )

        return data

    def _water_or_not(self, xx: xr.Dataset):
        # mark water freq > 0.5 as 1
        data = expr_eval(
            "where(a>0.5, 1, 0)",
            {"a": xx["wet_clear"].data},
            name="get_water",
            dtype="uint8",
        )

        # mark nans
        data = expr_eval(
            "where(a!=a, nodata, b)",
            {"a": xx["wet_clear"].data, "b": data},
            name="get_water",
            dtype="uint8",
            **{"nodata": int(NODATA)},
        )
        return data

    def _wet_or_not(self, xx: xr.Dataset):
        # mark water freq >= 0.5 as 1
        data = expr_eval(
            "where(a>0, 1, 0)",
            {"a": xx["wet_valid"].data},
            name="get_wet",
            dtype="uint8",
        )

        # mark nans
        data = expr_eval(
            "where(a!=a, nodata, b)",
            {"a": xx["wet_valid"].data, "b": data},
            name="get_wet",
            dtype="uint8",
            **{"nodata": int(NODATA)},
        )
        return data

    def _wet_valid_percent(self, data, nodata):
        wet = da.zeros(data.shape[1:], chunks=data.chunks[1:], dtype="uint8")
        total = da.zeros(data.shape[1:], chunks=data.chunks[1:], dtype="uint8")

        for t in data:
            # +1 if not nodata
            wet = expr_eval(
                "where(a==nodata, b, a+b)",
                {"a": t, "b": wet},
                name="get_wet",
                dtype="uint8",
                **{"nodata": nodata},
            )

            # total valid
            total = expr_eval(
                "where(a==nodata, b, b+1)",
                {"a": t, "b": total},
                name="get_total_valid",
                dtype="uint8",
                **{"nodata": nodata},
            )

        wet = expr_eval(
            "where(a<=0, nodata, b/a*100)",
            {"a": total, "b": wet},
            name="normalize_max_count",
            dtype="float32",
            **{"nodata": int(nodata)},
        )

        wet = da.ceil(wet).astype("uint8")
        return wet

    def _max_consecutive_months(self, data, nodata, normalize=False):
        tmp = da.zeros(data.shape[1:], chunks=data.chunks[1:], dtype="uint8")
        max_count = da.zeros(data.shape[1:], chunks=data.chunks[1:], dtype="uint8")
        total = da.zeros(data.shape[1:], chunks=data.chunks[1:], dtype="uint8")

        for t in data:
            # +1 if not nodata
            tmp = expr_eval(
                "where(a==nodata, b, a+b)",
                {"a": t, "b": tmp},
                name="compute_consecutive_month",
                dtype="uint8",
                **{"nodata": nodata},
            )

            # save the max
            max_count = expr_eval(
                "where(a>b, a, b)",
                {"a": max_count, "b": tmp},
                name="compute_consecutive_month",
                dtype="uint8",
            )

            # reset if not veg
            tmp = expr_eval(
                "where((a<=0), 0, b)",
                {"a": t, "b": tmp},
                name="compute_consecutive_month",
                dtype="uint8",
            )

            # total valid
            total = expr_eval(
                "where(a==nodata, b, b+1)",
                {"a": t, "b": total},
                name="get_total_valid",
                dtype="uint8",
                **{"nodata": nodata},
            )

        # mark nodata
        if normalize:
            max_count = expr_eval(
                "where(a<=0, nodata, b/a*12)",
                {"a": total, "b": max_count},
                name="normalize_max_count",
                dtype="float32",
                **{"nodata": int(nodata)},
            )
            max_count = da.ceil(max_count).astype("uint8")
        else:
            max_count = expr_eval(
                "where(a<=0, nodata, b)",
                {"a": total, "b": max_count},
                name="mark_nodata",
                dtype="uint8",
                **{"nodata": int(nodata)},
            )

        return max_count

    def reduce(self, xx: xr.Dataset) -> xr.Dataset:
        xx = xx.groupby("time.month").map(median_ds, dim="spec")

        # consecutive observation of veg
        veg_data = self._veg_or_not(xx)
        max_count_veg = self._max_consecutive_months(veg_data, NODATA)

        # consecutive observation of non-veg
        non_veg_data = expr_eval(
            "where(a<nodata, 1-a, nodata)",
            {"a": veg_data},
            name="invert_veg",
            dtype="uint8",
            **{"nodata": NODATA},
        )
        max_count_non_veg = self._max_consecutive_months(non_veg_data, NODATA)

        # non-veg < threshold implies veg >= threshold
        # implies any "wet" area potentially veg

        max_count_veg = expr_eval(
            "where((a<_v)&(b<_v), _v, b)",
            {"a": max_count_non_veg, "b": max_count_veg},
            name="clip_veg",
            dtype="uint8",
            **{"_v": self.veg_threshold},
        )

        data = self._water_or_not(xx)
        max_count_water = self._max_consecutive_months(data, NODATA, normalize=True)

        data = self._wet_or_not(xx)
        wet_percent = self._wet_valid_percent(data, NODATA)

        attrs = xx.attrs.copy()
        attrs["nodata"] = int(NODATA)
        data_vars = {
            k: xr.DataArray(v, dims=xx["pv"].dims[1:], attrs=attrs)
            for k, v in zip(
                self.measurements, [max_count_veg, max_count_water, wet_percent]
            )
        }
        coords = {dim: xx.coords[dim] for dim in xx["pv"].dims[1:]}
        return xr.Dataset(data_vars=data_vars, coords=coords, attrs=xx.attrs)


register("veg_count", StatsVegCount)
