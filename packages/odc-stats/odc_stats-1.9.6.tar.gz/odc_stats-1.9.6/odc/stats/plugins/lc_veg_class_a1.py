"""
Plugin of Module A1 in LandCover PipeLine
"""

import numpy as np
import xarray as xr
from odc.algo import expr_eval

from ._registry import StatsPluginInterface, register
from ._utils import replace_nodata_with_mode

NODATA = 255


class StatsDem(StatsPluginInterface):
    NAME = "ga_ls_lccs_(ni)dem"
    SHORT_NAME = NAME
    VERSION = "0.0.1"
    PRODUCT_FAMILY = "lccs"

    def native_transform(self, xx):
        # reproject cannot work with nodata being int for float
        # hence convert to nan

        for var in self.input_bands:
            nodata = float(xx[var].attrs["nodata"])
            data = expr_eval(
                "where(a>b, a, _nan)",
                {"a": xx[var].data},
                name="convert_nodata",
                dtype="float32",
                **{"_nan": np.nan, "b": nodata},
            )
            xx[var].data = data
            xx[var].attrs["nodata"] = np.nan

        return xx

    def reduce(self, xx: xr.Dataset) -> xr.Dataset:
        if self.measurements != self.input_bands:
            xx = xx.rename(dict(zip(self.input_bands, self.measurements)))
        return xx


class StatsVegClassL1(StatsPluginInterface):
    NAME = "ga_ls_lccs_veg_class_a1"
    SHORT_NAME = NAME
    VERSION = "0.0.1"
    PRODUCT_FAMILY = "lccs"

    def __init__(
        self,
        *,
        output_classes: dict,
        dem_threshold: int | None = None,
        mudflat_threshold: int | None = None,
        saltpan_threshold: int | None = None,
        water_threshold: float | None = None,
        veg_threshold: int | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dem_threshold = dem_threshold if dem_threshold is not None else 6
        self.mudflat_threshold = (
            mudflat_threshold if mudflat_threshold is not None else 1000
        )
        self.saltpan_threshold = (
            saltpan_threshold if saltpan_threshold is not None else 1500
        )
        self.water_threshold = water_threshold if water_threshold is not None else 0.2
        self.veg_threshold = veg_threshold if veg_threshold is not None else 2
        self.output_classes = output_classes

    def fuser(self, xx):
        return xx

    def l3_class(self, xx: xr.Dataset):
        si5 = expr_eval(
            "where(a>nodata, a*b/c, _nan)",
            {"a": xx.nbart_blue.data, "b": xx.nbart_red.data, "c": xx.nbart_green.data},
            name="caculate_si5",
            dtype="float32",
            **{"_nan": np.nan, "nodata": xx.nbart_blue.attrs["nodata"]},
        )

        # water  (water_freq >= 0.2)

        l3_mask = expr_eval(
            "where((a>=wt), m, 0)",
            {"a": xx["frequency"].data},
            name="mark_water",
            dtype="uint8",
            **{
                "wt": self.water_threshold,
                "m": self.output_classes["water"],
            },
        )

        # surface: (si5 > 1000 & dem <=6 ) | (si5 > 1500) | (veg_freq < 2) & !water
        # rest:  aquatic/terretrial veg
        l3_mask = expr_eval(
            "where(((a>mt)&(b<=dt)|(a>st)|(d<vt))&(c<=0), m, c)",
            {
                "a": si5,
                "b": xx.dem_h.data,
                "d": xx.veg_frequency.data,
                "c": l3_mask,
            },
            name="mark_surface",
            dtype="uint8",
            **{
                "mt": self.mudflat_threshold,
                "dt": self.dem_threshold,
                "st": self.saltpan_threshold,
                "vt": self.veg_threshold,
                "m": self.output_classes["surface"],
            },
        )

        # all unmarked values (0) and 255 > veg >= 2 is terretrial veg
        l3_mask = expr_eval(
            "where((a<=0)&(b<nodata), m, a)",
            {"a": l3_mask, "b": xx["veg_frequency"].data},
            name="mark_veg",
            dtype="uint8",
            **{
                "m": self.output_classes["terrestrial_veg"],
                "nodata": (
                    NODATA
                    if xx["veg_frequency"].attrs["nodata"]
                    != xx["veg_frequency"].attrs["nodata"]
                    else xx["veg_frequency"].attrs["nodata"]
                ),
            },
        )

        # if its mangrove or coast region
        for b in self.optional_bands:
            if b in xx.data_vars:
                if b == "elevation":
                    # intertidal: water | surface & elevation
                    # aquatic_veg: veg & elevation
                    data = expr_eval(
                        "where((a==a), 1, 0)",
                        {
                            "a": xx[b].data,
                        },
                        name="mark_intertidal",
                        dtype="bool",
                    )

                    l3_mask = expr_eval(
                        "where(a&((b==_w)|(b==_s)), m, b)",
                        {"a": data, "b": l3_mask},
                        name="intertidal_water",
                        dtype="uint8",
                        **{
                            "m": self.output_classes["intertidal"],
                            "_w": self.output_classes["water"],
                            "_s": self.output_classes["surface"],
                        },
                    )

                    l3_mask = expr_eval(
                        "where(a&(b==_v), m, b)",
                        {"a": data, "b": l3_mask},
                        name="intertidal_veg",
                        dtype="uint8",
                        **{
                            "m": self.output_classes["aquatic_veg_herb"],
                            "_v": self.output_classes["terrestrial_veg"],
                        },
                    )
                elif b == "canopy_cover_class":
                    # aquatic_veg: (mangroves > 0) & (mangroves != nodata)
                    # mangroves.nodata = 255 or nan
                    l3_mask = expr_eval(
                        "where((a>0)&((a<nodata)|(nodata!=nodata)), m, b)",
                        {"a": xx[b].data, "b": l3_mask},
                        name="mark_mangroves",
                        dtype="uint8",
                        **{
                            "nodata": xx[b].attrs["nodata"],
                            "m": self.output_classes["aquatic_veg_wood"],
                        },
                    )

        # all unmarked values (0) and wet_percentage != nodata is mode of neighbourhood
        target_value = 254
        l3_mask = expr_eval(
            "where((a<=0)&(b<nodata), _u, a)",
            {"a": l3_mask, "b": xx["wet_percentage"].data},
            name="mark_other_valid",
            dtype="uint8",
            **{
                "nodata": (
                    NODATA
                    if xx["wet_percentage"].attrs["nodata"]
                    != xx["wet_percentage"].attrs["nodata"]
                    else xx["wet_percentage"].attrs["nodata"]
                ),
                "_u": target_value,
            },
        )
        l3_mask = replace_nodata_with_mode(
            l3_mask.squeeze(0),
            target_value=target_value,
            exclude_values=[0],
            neighbourhood_size=5,
        )

        # Mask nans and pixels where non of classes applicable
        l3_mask = expr_eval(
            "where((e<=0)|(e==254)|(g!=g), nodata, e)",
            {
                "e": l3_mask,
                "g": si5.squeeze(0),
            },
            name="mark_nodata",
            dtype="uint8",
            **{"nodata": NODATA},
        )

        return l3_mask

    def reduce(self, xx: xr.Dataset) -> xr.Dataset:
        l3_mask = self.l3_class(xx)
        attrs = xx.attrs.copy()
        attrs["nodata"] = int(NODATA)
        data_vars = {
            k: xr.DataArray(v, dims=xx["veg_frequency"].dims[1:], attrs=attrs)
            for k, v in zip(self.measurements, [l3_mask])
        }
        coords = {dim: xx.coords[dim] for dim in xx["veg_frequency"].dims[1:]}
        return xr.Dataset(data_vars=data_vars, coords=coords, attrs=xx.attrs)


register("veg_class_l1", StatsVegClassL1)
register("dem_in_stats", StatsDem)
