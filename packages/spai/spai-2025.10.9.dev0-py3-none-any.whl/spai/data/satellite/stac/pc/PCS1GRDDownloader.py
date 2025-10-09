"""
PCS1GRDDownloader class to download and load Sentinel-1 GRD data from a STAC API of the Planetary Computer.
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


S1_BANDS = [
    "vv",
    "vh",
]


class PCS1GRDDownloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = S1_BANDS,
        resolution: Optional[float] = 0.000045045,
        crs: Optional[str] = "EPSG:4326",
    ):
        # TODO add filters
        # See filters in https://earth-search.aws.element84.com/v1/collections/sentinel-1-grd/items
        query = {}
        super().__init__(aoi, datetime, query)
        self.collection = "sentinel-1-grd"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
