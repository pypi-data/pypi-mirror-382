"""
Utility functions for the satellite data module
"""

import os
from warnings import warn
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from typing import Optional, Tuple, Any

from .stac.decorators import with_geopandas, with_geojson, with_requests


def validate_coords(coords):
    """
    Validate the coordinates of a polygon

    Parameters
    ----------
    coords : list
        List of coordinates of a polygon: [[lon1,lat1],[lon2,lat2], ... ,[lonN,latN]]

    Returns
    -------
    list
        List of coordinates of a polygon: [[lon1,lat1],[lon2,lat2], ... ,[lonN,latN]]

    Raises
    ------
    Exception
        If coords is not a list of coordinates
        If each coord is not a list of 2 coordinates
        If each coordinate is not a float
        If each latitude is not a valid lat/long
        If each longitude is not a valid lat/long
    """
    for coord in coords:
        # check that each coord is a list of 2 coordinates
        if len(coord) != 2:
            raise Exception("each coord must be a list of 2 coordinates")
        # check that each coordinate is a float
        if not isinstance(coord[0], float) or not isinstance(coord[1], float):
            raise Exception("each coordinate must be a float")
        lon = coord[0]
        lat = coord[1]

        # check lat and long ranges
        if lon < -180 or lon > 180 or lat < -90 or lat > 90:
            raise Exception("each coordinate must be a valid lat/long")

    return coords


def validate_bounds(bounds):
    """
    Validate the bounds of a polygon

    Parameters
    ----------
    bounds : tuple
        Tuple of bounds: (minlon, minlat, maxlon, maxlat)

    Returns
    -------
    tuple
        Tuple of bounds: (minlon, minlat, maxlon, maxlat)

    Raises
    ------
    Exception
        If bounds is not a tuple of 4 points
        If each bound is not a float
        If each latitude is not a valid lat/long
        If each longitude is not a valid lat/long
        If minlat is not less than maxlat or minlng is not less than maxlng
    """
    # check that bounds is a list
    if len(bounds) != 4 or not isinstance(bounds, tuple):
        raise Exception(
            "bounds must be a tuple of 4 points: (minlon, minlat, maxlon, maxlat))"
        )
    # check that each bound is a float
    for bound in bounds:
        if not isinstance(bound, float):
            raise Exception("each bound must be a float")
    # check lat and long ranges
    minlon = bounds[0]
    minlat = bounds[1]
    maxlon = bounds[2]
    maxlat = bounds[3]

    if minlat < -90 or minlat > 90 or maxlat < -90 or maxlat > 90:
        raise Exception("each latitude must be a valid lat/long")
    if minlon < -180 or minlon > 180 or maxlon < -180 or maxlon > 180:
        raise Exception("each longitude must be a valid lat/long")
    # check that minlat < maxlat and minlng < maxlng
    if minlon > maxlon or minlat > maxlat:
        raise Exception(
            "minlat must be less than maxlat and minlng must be less than maxlng"
        )
    return bounds


@with_geopandas
@with_geojson
def create_aoi_geodataframe(obj, crs="EPSG:4326"):
    """
    Create a GeoDataFrame of the Bounding Box of the obj

    Parameters
    ----------
    obj : Any
        The area of interest which can be specified in various formats. Obj can be a:
        - GeoDataFrame
        - GeoJSON file
        - Path to a GeoJSON file
        - Polygon of Shapely (Bounding Box)
        - List of Coords of a (Bounding Box)
        - Location name (string)
    crs : str, optional
        Coordinate reference system to be used for the images, by default "EPSG:4326"

    Returns
    -------
    GeoDataFrame
        A GeoDataFrame of the Bounding Box of the obj

    Raises
    ------
    Exception
        If the location is not supported
    """
    import geopandas as gpd
    import geojson
    from shapely.geometry import box, Polygon

    # return a GeoDataFrame of the Bounding Box of the obj or a list of gdfs if obj is a location name and there are more than one relation
    gdf = gpd.GeoDataFrame()

    if (
        isinstance(obj, str)
        and not os.path.isfile(obj)
        and not obj.endswith(".geojson")
    ):
        # case 1: obj is a location name (e.g. "Madrid")
        gdf = get_box_or_gdfs_by_place_name(
            obj
        )  # return GeoDataFrame of the Bounding Box of the location

    elif isinstance(obj, list):
        # case 2: obj is a list of coords of a Polygon: [[lat1,long1],[lat2,long2],...,[latN,longN]]
        coords = validate_coords(obj)
        poly = Polygon(coords)
        bounds = poly.bounds
        obj = box(*bounds)  # return Box of Shapely

    if isinstance(obj, tuple):
        # case 3: obj is a tuple of bounds: (minlat, minlng, maxlat, maxlng)
        bounds = validate_bounds(obj)
        obj = box(*bounds)  # return Box of Shapely

    if isinstance(obj, Polygon):
        # case 4: obj is a Box of Shapely: Polygon[[lat1,long1],[lat2,long2],[lat3,long3],[lat4,long4]]
        bounds = obj.bounds
        validate_bounds(bounds)
        gdf = gpd.GeoDataFrame(geometry=[obj], crs=4326)

    if isinstance(obj, gpd.GeoDataFrame):
        # case 5: obj is a GeoDataFrame
        gdf = obj

    if (
        isinstance(obj, dict)
        and obj.get("type") == "FeatureCollection"
        and "features" in obj
    ):
        # case 6: obj is a GeoJSON file
        if obj["type"] == "Polygon":
            for coords in obj["coordinates"][0]:
                validate_coords(coords)
        elif obj["type"] == "MultiPolygon":
            for _coords in obj["coordinates"][0]:
                for coords in _coords:
                    validate_coords(coords)
        gdf = gpd.GeoDataFrame.from_features(obj, crs=4326)

    if isinstance(obj, str) and os.path.isfile(obj) and obj.endswith(".geojson"):
        # case 7: obj is a path to GeoJSON file
        geojson_file = geojson.load(open(obj))
        if geojson_file["type"] == "Polygon":
            for coords in geojson_file["coordinates"][0]:
                validate_coords(coords)
        elif geojson_file["type"] == "MultiPolygon":
            for _coords in geojson_file["coordinates"][0]:
                for coords in _coords:
                    validate_coords(coords)
        gdf = gpd.GeoDataFrame.from_features(geojson_file, crs=4326)

    if not gdf.crs:
        warn("GeoDataFrame has no crs, assuming EPSG:4326")
        gdf = gdf.set_crs(epsg=4326)
    if gdf.crs != crs:
        gdf = gdf.to_crs(crs)

    if gdf.empty:
        raise Exception(f"Location {obj} not supported")

    if is_valid_geodataframe(gdf):
        return gdf


@with_geopandas
@with_requests
def get_bb_by_city_name(city_name):
    """
    Get the bounding box of a city by its name

    Parameters
    ----------
    city_name : str

    Returns
    -------
    list
        List of bounding boxes of the city

    Raises
    ------
    Exception
        If no results found
    """
    import requests
    from shapely.geometry import box

    base_url = "https://nominatim.openstreetmap.org"
    format_out = "json"
    limit = 10

    # Construct the API request URL
    url = f"{base_url}/search?city={city_name}&format={format_out}&limit={limit}"

    # Send the API request
    headers = {
        "User-Agent": "SPAI (info@earthpulse.ai)"
    }  # Set the User-Agent to avoid being blocked
    response = requests.get(url, headers=headers, timeout=30).json()

    results = []
    if len(response) == 0:
        raise Exception("No results found")
    for result in response:
        if "boundingbox" in result:
            bounding_box = result["boundingbox"]
            if len(bounding_box) == 4:
                min_lon, max_lon, min_lat, max_lat = map(float, bounding_box)
                results.append(
                    {
                        "name": f"{result['display_name']}",
                        "bbox": box(min_lat, min_lon, max_lat, max_lon),
                    }
                )

    return results


@with_geopandas
def get_box_or_gdfs_by_place_name(place_name):
    """
    Get the bounding box of a place by its name

    Parameters
    ----------
    place_name : str

    Returns
    -------
    GeoDataFrame
        GeoDataFrame of the Bounding Box of the place

    Raises
    ------
    Exception
        If place_name is not a string
    """
    import geopandas as gpd

    if not isinstance(place_name, str):
        raise Exception("place_name must be a string")
    results = get_bb_by_city_name(place_name)

    if len(results) == 0:
        return None
    else:
        # Always return the first result as gdf
        first_result = results[0]
        gdf = gpd.GeoDataFrame({"name": [place_name]})
        gdf.set_geometry([first_result["bbox"]], inplace=True)
        gdf.set_crs(epsg=4326, inplace=True)

        return gdf


def is_valid_geodataframe(gdf) -> bool:
    """
    Check if the given GeoDataFrame is valid

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame to validate

    Returns
    -------
    bool
        True if the GeoDataFrame is valid, False otherwise

    Raises
    ------
    ValueError
        If the geometry is not valid
        If the area of the AoI is greater than 20 km2
    """
    if len(gdf) != 1:
        raise ValueError("AoI must be a single polygon or area, not multiple polygons")

    if not gdf.geometry.is_valid.all():
        raise ValueError("The given geometry is not valid")

    return True


def is_valid_datetime_param(param: Any):
    """
    Check if the given parameter is a valid datetime parameter

    Parameters
    ----------
    param : Any
        Date to validate

    Returns
    -------
    bool
        True if the parameter is a valid datetime parameter, False otherwise

    Raises
    ------
    ValueError
        If the parameter is not a valid datetime parameter
    """
    if isinstance(param, datetime):
        return True
    elif isinstance(param, str):
        try:
            isoparse(param)
            return True
        except ValueError:
            try:
                datetime.strptime(param, "%Y-%m-%d")
                return True
            except ValueError:
                try:
                    datetime.strptime(param, "%Y-%m")
                    return True
                except ValueError:
                    try:
                        datetime.strptime(param, "%Y")
                        return True
                    except ValueError:
                        return False
    elif isinstance(param, (list, tuple)) and len(param) == 2:
        if isinstance(param[0], (datetime, str)) and isinstance(
            param[1], (datetime, str)
        ):
            return True
    elif isinstance(param, str) and "/" in param:
        parts = param.split("/")
        if len(parts) == 2:
            for part in parts:
                if part.strip() == "..":
                    return True
                else:
                    try:
                        isoparse(part.strip())
                    except ValueError:
                        return False
            return True
    return False


def is_valid_date(date_str: str) -> bool:
    """
    Check if a date is valid

    Parameters
    ----------
    date_str : str
        Date to validate

    Returns
    -------
    bool
        True if the date is valid, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_time_interval(time_interval: list) -> bool:
    """
    Check if is time interval and is valid

    Parameters
    ----------
    time_interval : list
        List of two dates

    Returns
    -------
    bool
        True if the time interval is valid, False otherwise
    """
    if not isinstance(time_interval, (list, tuple)) or len(time_interval) != 2:
        return False

    for value in time_interval:
        if not isinstance(value, str):
            return False
        if not is_valid_date(value):
            return False

    return True


def format_datetime_param(date):
    """
    Prepare time interval to request data

    Parameters
    ----------
    date : Union[str, datetime, Tuple[str, str]]
        Date to format

    Returns
    -------
    Tuple[str, str]
        Time interval formatted
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    elif isinstance(date, tuple):
        if is_time_interval(date):
            return date
        else:
            raise ValueError(
                "The time interval must be a range of two dates, with format YYYY-MM-DD or a datetime object"
            )
    elif not isinstance(date, datetime):
        raise ValueError(
            "The date must be a string with format YYYY-MM-DD or a datetime object"
        )

    date_day_before = date - timedelta(days=1)
    date_next_day = date + timedelta(days=1)

    date_day_before_str = date_day_before.strftime("%Y-%m-%d")
    date_next_day_str = date_next_day.strftime("%Y-%m-%d")

    return (date_day_before_str, date_next_day_str)


def get_last_month(starting_date: Optional[str] = None) -> Tuple[str, str]:
    """
    Get the last month time interval

    Parameters
    ----------
    starting_date : Optional[str], optional
        Starting date, by default None

    Returns
    -------
    Tuple[str, str]
        Time interval of the last month
    """
    if not starting_date:
        now = datetime.now()
    elif starting_date and isinstance(starting_date, tuple):
        now = isoparse(starting_date[0])
    last_months = now - timedelta(days=30)
    time_interval = (last_months.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))

    if is_valid_datetime_param(time_interval):
        return time_interval


def add_item_extra_properties(item, item_dict, query_properties, query_parameters):
    """
    Add extra properties to the item dictionary

    Parameters
    ----------
    item : Any
        Item to get the properties
    item_dict : dict
        Dictionary to add the properties
    query_properties : list
        List of properties to add
    query_parameters : dict
        Dictionary of query parameters

    Returns
    -------
    dict
        Dictionary with the extra properties added
    """
    for parameter in query_parameters.keys():
        for prop in query_properties:
            if parameter in prop:
                item_dict[prop] = item.properties[prop]

    return item_dict
