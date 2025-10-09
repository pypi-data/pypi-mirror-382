from .SHDownloader import SHDownloader
from sentinelhub import MosaickingOrder, DataCollection


class SHCloudMaskDownloader(SHDownloader):
    def __init__(self, download_folder):
        super().__init__(download_folder)
        self.resolution = 10  # mpp
        self.data_collection = DataCollection.SENTINEL2_L1C
        self.mosaicking_order = MosaickingOrder.LEAST_CC
        self.script = """
            //VERSION=3
            function setup() {
            return {
                input: ["CLM", "CLP"],
                output: { bands: 2, sampleType: "UINT8" }
            }
            }
            function evaluatePixel(sample) {
            return [ sample.CLM, sample.CLP ];
            }
            """
