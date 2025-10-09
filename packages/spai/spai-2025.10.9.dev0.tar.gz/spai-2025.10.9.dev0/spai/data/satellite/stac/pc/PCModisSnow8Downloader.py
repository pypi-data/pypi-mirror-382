"""
PCModisSnow8Downloader class to download and load MODIS Snow Cover 8-day data from a STAC API of the Planetary Computer.

https://planetarycomputer.microsoft.com/dataset/modis-10A2-061
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


MODIS_SNOW_8_BANDS = ["Maximum_Snow_Extent", "Eight_Day_Snow_Cover"]


class PCModisSnow8Downloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = MODIS_SNOW_8_BANDS,
        resolution: Optional[float] = 0.00587,
        crs: Optional[str] = "EPSG:4326",
    ):
        # TODO add filters
        query = {}
        super().__init__(aoi, datetime, query)
        self.collection = "modis-10A2-061"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
