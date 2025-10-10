from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import hats.pixel_math.healpix_shim as hp
from hats import read_hats
from hats.catalog import TableProperties
from hats.io.validation import is_valid_catalog
from hats.pixel_math.healpix_pixel import HealpixPixel
from upath import UPath

from hats_import.runtime_arguments import RuntimeArguments


@dataclass
class MarginCacheArguments(RuntimeArguments):
    """Container for margin cache generation arguments"""

    margin_threshold: float = 5.0
    """the size of the margin cache boundary, given in arcseconds. If the `margin_order` parameter is set
    and fine_filtering is not run, the `margin_order` will be used to determine the margin and this 
    value will be overwritten."""
    margin_order: int = -1
    """the order of healpixels that will be used to generate the margin of each catalog pixel. By default, 
    this is calculated from `margin_threshold` to be the minimum order that covers the entire 
    threshold. If this is set and there is no fine filtering, the `margin_threshold` will be recalculated to 
    be the minimum distance of the specified order."""
    fine_filtering: bool = False
    """should we perform the precise boundary checking? if false, some results may be
    greater than `margin_threshold` away from the border (but within `margin_order`)."""

    input_catalog_path: str | Path | UPath | None = None
    """the path to the hats-formatted input catalog."""
    debug_filter_pixel_list: list[HealpixPixel] = field(default_factory=list)
    """debug setting. if provided, we will first filter the catalog to the pixels
    provided. this can be useful for creating a margin over a subset of a catalog."""

    def __post_init__(self):
        self._check_arguments()

    def _check_arguments(self):
        super()._check_arguments()
        if not self.input_catalog_path:
            raise ValueError("input_catalog_path is required")
        if not is_valid_catalog(self.input_catalog_path):
            raise ValueError("input_catalog_path not a valid catalog")

        self.catalog = read_hats(self.input_catalog_path)
        if len(self.debug_filter_pixel_list) > 0:
            self.catalog = self.catalog.filter_from_pixel_list(self.debug_filter_pixel_list)
            if len(self.catalog.get_healpix_pixels()) == 0:
                raise ValueError("debug_filter_pixel_list has created empty catalog")
        if not self.catalog.has_healpix_column():
            raise ValueError("Only catalogs with some healpix column (e.g. _healpix_29) can have a margin")

        if self.fine_filtering:
            raise NotImplementedError("Fine filtering temporarily removed.")

        highest_order = int(self.catalog.partition_info.get_highest_order())

        if self.margin_order >= 0 and not self.fine_filtering:
            self.margin_threshold = hp.order2mindist(self.margin_order) * 60.0

        if self.margin_order < 0:
            self.margin_order = hp.margin2order(margin_thr_arcmin=self.margin_threshold / 60.0)

        if self.margin_order < highest_order + 1:
            raise ValueError(
                "margin_order must be of a higher order than the highest order catalog partition pixel."
            )

        margin_pixel_mindist = hp.order2mindist(self.margin_order)
        if margin_pixel_mindist * 60.0 < self.margin_threshold:
            raise ValueError("margin pixels must be larger than margin_threshold")

    def to_table_properties(
        self, total_rows: int, highest_order: int, moc_sky_fraction: float
    ) -> TableProperties:
        """Catalog-type-specific dataset info."""
        info = {
            "catalog_name": self.output_artifact_name,
            "total_rows": total_rows,
            "catalog_type": "margin",
            "ra_column": self.catalog.catalog_info.ra_column,
            "dec_column": self.catalog.catalog_info.dec_column,
            "primary_catalog": str(self.input_catalog_path),
            "margin_threshold": self.margin_threshold,
            "hats_order": highest_order,
            "moc_sky_fraction": f"{moc_sky_fraction:0.5f}",
            "hats_col_healpix": self.catalog.catalog_info.healpix_column,
            "hats_col_healpix_order": self.catalog.catalog_info.healpix_order,
        } | self.extra_property_dict()
        return TableProperties(**info)
