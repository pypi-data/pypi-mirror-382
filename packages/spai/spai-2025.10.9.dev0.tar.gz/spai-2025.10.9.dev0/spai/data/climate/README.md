See https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation#heading-Parameterlistings for the different vars you can download. 

### Auth

You need to set a PAT code in your .env The PAT code can be retrieved by creating an account on https://earthdatahub.destine.eu/

### Getting started

```
from datetime import datetime

from spai.spai.data.climate.reanalysis_land_era5 import download_reanalysis_land_era5
from spai.spai.data.climate.area_of_interest import AreaOfInterest
from spai.spai.storage.LocalStorage import LocalStorage

my_storage = LocalStorage("./temp",)

aoi = AreaOfInterest(
    xmin=10.0,
    xmax=11.0,
    ymin=45.0,
    ymax=46.0,
)

# or AreaOfInterest.from_geodataframe(my_gdf)

start_date = datetime(2020, 1, 1).date()
end_date = datetime(2020, 1, 2).date()

data = load_reanalysis_land_era5(
    storage=my_storage,
    aoi=aoi,
    start_date=start_date,
    end_date=end_date,
    era5_vars=['t2m', 'tp'],
)
```

Then the data can be clipped/edited and then downloaded to the set storage after inspection:

```
# eg only take full accumulated values at 00:00
data.data = data.data.sel(valid_time=data.data.valid_time.dt.hour == 0)

path = data.download('my_download.zarr')
```
