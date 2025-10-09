from .SHS5PDownloader import SHS5PDownloader


class SHS5PNO2Downloader(SHS5PDownloader):
    def __init__(self, download_folder):
        super().__init__(download_folder)
        self.script = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["NO2"],
                        units: "DN"
                    }],
                    output: {
                        id: "default",
                        bands: 2,
                        sampleType: "FLOAT32"
                    }
                };
            }

            function evaluatePixel(sample) {
                return [sample.NO2];
            }
        """
