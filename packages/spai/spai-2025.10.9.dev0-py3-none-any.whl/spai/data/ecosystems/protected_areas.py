from typing import Optional, Any
import geopandas as gpd
from ..sources.osm import load_osm_data
from ..satellite.utils import create_aoi_geodataframe


def load_protected_areas(
    aoi: Any,
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "boundary": "protected_area",
        "leisure": "nature_reserve",
    },
    crs: Optional[str] = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load protected area elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes protected areas and nature reserves.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the protected area geometries
    """
    gdf = create_aoi_geodataframe(aoi)

    if source == "osm":
        return load_osm_data(
            gdf, query, geometry_types=["Polygon", "MultiPolygon"], crs=crs
        )
    else:
        raise ValueError("Unsupported source")


def download_protected_areas(
    storage,
    aoi: Any,
    name: Optional[str] = "protected_areas.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "boundary": "protected_area",
        "leisure": "nature_reserve",
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download protected area elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    name : str, optional
        The name of the file to store protected area geometries, by default "protected_areas.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes protected areas and nature reserves.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    final_protected_areas_gdf = load_protected_areas(aoi, source, query, crs)
    if not final_protected_areas_gdf.empty:
        storage.create(final_protected_areas_gdf, name=name)
