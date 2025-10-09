"""
PCAlosPalsarAnnualDownloader class to download and load ALOS PALSAR Annual mosaic data from a STAC API of the Planetary Computer.

https://planetarycomputer.microsoft.com/dataset/alos-palsar-mosaic
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


ALOS_PALSAR_ANNUAL_BANDS = ["HH", "HV"]


class PCAlosPalsarAnnualDownloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = ALOS_PALSAR_ANNUAL_BANDS,
        resolution: Optional[float] = 0.000293,
        crs: Optional[str] = "EPSG:4326",
    ):
        # TODO add filters
        query = {}
        super().__init__(aoi, datetime, query)
        self.collection = "alos-palsar-mosaic"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
