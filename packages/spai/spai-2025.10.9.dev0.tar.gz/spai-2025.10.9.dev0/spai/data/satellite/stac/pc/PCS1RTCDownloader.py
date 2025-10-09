"""
PCS1RTCDownloader class to download and load Sentinel-1 RTC data from a STAC API of the Planetary Computer.

https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc
"""

from .PCDownloader import PCDownloader

from typing import Optional, List


S1_BANDS = [
    "vv",
    "vh",
]


class PCS1RTCDownloader(PCDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = S1_BANDS,
        resolution: Optional[float] = 0.000045045,
        crs: Optional[str] = "EPSG:4326",
    ):
        # TODO add filters
        query = {}
        super().__init__(aoi, datetime, query)
        self.collection = "sentinel-1-rtc"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs
