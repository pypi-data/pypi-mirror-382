from datetime import date
from pathlib import Path
import dotenv
import os
import numpy as np
import xarray as xr

from ...storage import Storage
from .area_of_interest import AreaOfInterest

dotenv.load_dotenv()


PAT = os.getenv(
    "EARTH_DATA_HUB_PAT"
  )  #  https://earthdatahub.destine.eu/account-settings
MAX_DOWNLOAD_SIZE_MB = 5000
ERA5_VARS = ["asn", "d2m", "e", "es", "evabs", "evaow", "evatc", 
    "evavt", "fal", "lai_hv", "lai_lv", "lblt", "licd", "lict", "lmld", "lmlt", 
    "lshf", "ltlt", "pev", "ro", "rsn", "sde", "sf", "skt", "slhf", "smlt", 
    "snowc", "sp", "src", "sro", "sshf", "ssr", "ssrd", "ssro", "stl1", "stl2", 
    "stl3", "stl4", "str", "strd", "swvl1", "swvl2", "swvl3", "swvl4", "t2m", 
    "tp", "tsn", "u10", "v10"]


class LoadedData:
    def __init__(self, data: xr.Dataset):
        self.data = data

    def download(self, name: str, storage: Storage) -> Path:
        if self.data.nbytes / 1e6 > MAX_DOWNLOAD_SIZE_MB:
            raise ValueError(
                f"Data request larger than {MAX_DOWNLOAD_SIZE_MB}MB, please select a smaller area, shorter the time range, or reduce the temporal or sp"
            )

        print(f"Downloading {(self.data.nbytes / 1e6,)} MB")

        data = self.data.compute()
        path = storage.create(
            data,
            name=name,
        )

        print(f"Data downloaded to {path}")
        return Path(path)


def load_reanalysis_land_era5(
    aoi: AreaOfInterest,
    start_date: date,
    end_date: date | None = None,
    era5_vars: list[str, None] = [],
) -> xr.Dataset:
    f"""
    For env vars see https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation#heading-Parameterlistings
    ERA5 vars available: {ERA5_VARS}
    """

    if end_date is None:
        end_date = start_date

    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end_date")

    if era5_vars and not set(era5_vars).issubset(ERA5_VARS):
        raise ValueError(f"At least one of the passed vars is not in allowed vars: {ERA5_VARS}")

    if not PAT:
        raise ValueError(
            "No PAT found for Earth Data Hub, please set EARTH_DATA_HUB_PAT on https://earthdatahub.destine.eu/ and store in your .env"
        )

    ds = xr.open_dataset(
        f"https://edh:{PAT}@data.earthdatahub.destine.eu/era5/reanalysis-era5-land-no-antartica-v0.zarr",
        storage_options={"client_kwargs": {"trust_env": True}},
        chunks={},
        engine="zarr",
    )

    data = ds.sel(
        valid_time=slice(
            np.datetime64(start_date), np.datetime64(end_date) + np.timedelta64(1, "D")
        ),
        latitude=slice(aoi.ymax, aoi.ymin),
        longitude=slice(aoi.xmin, aoi.xmax),
    )

    if era5_vars:
        data = data[era5_vars]

    if data.valid_time.size == 0:
        raise ValueError("No data available to download for the specified date range")

    return LoadedData(data=data)
