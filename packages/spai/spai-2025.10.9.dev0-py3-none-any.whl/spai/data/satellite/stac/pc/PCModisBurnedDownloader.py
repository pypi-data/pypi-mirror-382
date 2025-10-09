"""
PCModisBurnedDownloader class to download and load MODIS Burned Area Monthly data from a STAC API of the Planetary Computer.

https://planetarycomputer.microsoft.com/dataset/modis-64A1-061
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


MODIS_BURNED_BANDS = [
    "QA",
    "Last_Day",
    "Burn_Date",
    "First_Day",
    "Burn_Date_Uncertainty",
]


class PCModisBurnedDownloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = MODIS_BURNED_BANDS,
        resolution: Optional[float] = 0.00587,
        crs: Optional[str] = "EPSG:4326",
    ):
        # TODO add filters
        query = {}
        super().__init__(aoi, datetime, query)
        self.collection = "modis-64A1-061"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
