from ..SHDownloader import SHDownloader


class SHS5PDownloader(SHDownloader):
    def __init__(self, download_folder):
        try:
            from sentinelhub import DataCollection
        except ImportError:
            raise ImportError(
                "The sentinelhub package is required. Please install it with 'pip install sentinelhub' and try again."
            )
        super().__init__(download_folder)
        self.data_collection = DataCollection.SENTINEL5P
        self.mosaicking_order = None
        self.resolution = (5500, 3500)
