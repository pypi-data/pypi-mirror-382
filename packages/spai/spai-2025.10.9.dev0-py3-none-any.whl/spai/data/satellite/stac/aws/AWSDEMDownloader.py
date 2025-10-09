from .AWSDownloader import AWSDownloader

from typing import Optional


class AWSDEMDownloader(AWSDownloader):
    def __init__(self, aoi, datetime=None):
        super().__init__(aoi, datetime)

    def search_stac(self):
        items = self.catalog.search(
            bbox=self.aoi,
            collections=self.collection,
        ).item_collection()

        if len(items) == 0:
            print(f"No {self.collection} found for the AoI")
            return None

        return items

    def load_stac(
        self,
        chunks: Optional[dict] = {"time": 5, "x": 512, "y": 512},
    ):
        items = self.search_stac()
        if not items:
            return None
        data = self.load(
            items,
            chunks=chunks,
            crs=self.crs,
            resolution=self.resolution,
            bbox=self.aoi,
        )

        return data
