"""
PCLandsat8Downloader class to download and load Landsat 8 data from a STAC API of the Planetary Computer.

https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


LANDSAT_8_BANDS = ["coastal", "blue", "green", "red", "nir08", "swir16", "swir22"]


class PCLandsat8Downloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = LANDSAT_8_BANDS,
        resolution: Optional[float] = 0.0000275,
        crs: Optional[str] = "EPSG:4326",
        cloud_cover: Optional[float] = 100,
    ):
        # TODO add filters
        query = {
            "eo:cloud_cover": {"lt": cloud_cover},
        }
        super().__init__(aoi, datetime, query)
        self.collection = "landsat-8-c2-l2"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
