from .AWSDEMDownloader import AWSDEMDownloader

from typing import Optional


class AWSDEM90Downloader(AWSDEMDownloader):
    def __init__(
        self,
        aoi,
        datetime=None,
        resolution: Optional[float] = 0.0009,
        crs: Optional[str] = "EPSG:4326",
    ):
        super().__init__(aoi, datetime)
        self.collection = "cop-dem-glo-90"
        self.datetime = datetime
        self.resolution = resolution
        self.crs = crs
