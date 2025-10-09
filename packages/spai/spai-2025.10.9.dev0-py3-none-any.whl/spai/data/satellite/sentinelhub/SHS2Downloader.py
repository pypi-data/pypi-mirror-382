from .SHDownloader import SHDownloader


class SHS2Downloader(SHDownloader):
    def __init__(self, download_folder):
        try:
            from sentinelhub import MosaickingOrder
        except ImportError:
            raise ImportError(
                "The sentinelhub package is required. Please install it with 'pip install sentinelhub' and try again."
            )
        super().__init__(download_folder)
        self.resolution = 10  # mpp
        self.mosaicking_order = MosaickingOrder.LEAST_CC
