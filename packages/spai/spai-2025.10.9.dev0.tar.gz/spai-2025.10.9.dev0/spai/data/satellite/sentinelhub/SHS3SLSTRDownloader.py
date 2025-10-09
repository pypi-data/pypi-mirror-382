from .SHDownloader import SHDownloader


class SHS3SLSTRDownloader(SHDownloader):
    def __init__(self, download_folder):
        try:
            from sentinelhub import DataCollection
        except ImportError:
            raise ImportError(
                "The sentinelhub package is required. Please install it with 'pip install sentinelhub' and try again."
            )
        super().__init__(download_folder)
        self.data_collection = DataCollection.SENTINEL3_SLSTR
        self.resolution = 1000
        # Only downloads TIR bands, see https://docs.sentinel-hub.com/api/latest/data/sentinel-3-slstr-l1b/examples/#tir-bands-as-a-geotiff-epsg-32632
        self.script = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["S7", "S8", "S9", "F1", "F2"]
                    }],
                    output: {
                        bands: 6,
                        sampleType: "UINT16" //floating point values are automatically rounded to the nearest integer by the service.
                    }
                };
            }

            function evaluatePixel(sample) {
                return [
                    sample.S7, sample.S8, sample.S9, sample.F1, sample.F2, sample.dataMask
                ];
            }
            """
