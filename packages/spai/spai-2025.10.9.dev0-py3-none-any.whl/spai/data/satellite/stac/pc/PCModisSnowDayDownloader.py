"""
PCModisSnowDayDownloader class to download and load MODIS Snow Cover Daily data from a STAC API of the Planetary Computer.

https://planetarycomputer.microsoft.com/dataset/modis-10A1-061
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


MODIS_SNOW_DAY_BANDS = ["NDSI", "NDSI_Snow_Cover", "Snow_Albedo_Daily_Tile"]


class PCModisSnowDayDownloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = MODIS_SNOW_DAY_BANDS,
        resolution: Optional[float] = 0.00587,
        crs: Optional[str] = "EPSG:4326",
    ):
        # TODO add filters
        query = {}
        super().__init__(aoi, datetime, query)
        self.collection = "modis-10A1-061"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
