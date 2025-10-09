from typing import Optional, Any

import geopandas as gpd
from ..sources.osm import load_osm_data
from ..satellite.utils import create_aoi_geodataframe


def load_buildings(
    aoi: Any,
    source: Optional[str] = "osm",
    query: Optional[dict] = {"building": True},
    crs: Optional[str] = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load the buildings from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default {"building": True}
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the building geometries
    """
    gdf = create_aoi_geodataframe(aoi, crs)

    if source == "osm":
        return load_osm_data(
            gdf, query, geometry_types=["Polygon", "MultiPolygon"], crs=crs
        )
    else:
        raise ValueError("Unsupported source")


def download_buildings(
    storage,
    aoi: Any,
    name: Optional[str] = "buildings.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {"building": True},
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download the buildings from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    name : str, optional
        The name of the file to store building geometries, by default "buildings.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default {"building": True}
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    final_buildings_gdf = load_buildings(aoi, source, query, crs)
    if not final_buildings_gdf.empty:
        storage.create(final_buildings_gdf, name=name)
