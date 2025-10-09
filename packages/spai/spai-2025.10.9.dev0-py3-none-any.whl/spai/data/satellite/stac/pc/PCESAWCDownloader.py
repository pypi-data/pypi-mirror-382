"""
PCESAWCDownloader class to download and load ESA Worldcover data from a STAC API of the Planetary Computer.
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


class PCESAWCDownloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = "map",
        resolution: Optional[float] = 0.0001,
        crs: Optional[str] = "EPSG:4326",
    ):
        # See filters in https://earth-search.aws.element84.com/v1/collections/sentinel-1-grd/items
        query = {}
        super().__init__(aoi, datetime, query)
        self.collection = "esa-worldcover"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
