from typing import Optional, Any
import geopandas as gpd
from ..sources.osm import load_osm_data
from ..satellite.utils import create_aoi_geodataframe


def load_waterways(
    aoi: Any,
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "waterway": ["river", "canal", "stream", "brook", "ditch", "drain"]
    },
    crs: Optional[str] = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load waterway elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes rivers, canals, streams, brooks, ditches, and drains.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the waterway geometries
    """
    gdf = create_aoi_geodataframe(aoi)

    if source == "osm":
        return load_osm_data(
            gdf, query, geometry_types=["LineString", "MultiLineString"], crs=crs
        )
    else:
        raise ValueError("Unsupported source")


def download_waterways(
    storage,
    aoi: Any,
    name: Optional[str] = "waterways.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "waterway": ["river", "canal", "stream", "brook", "ditch", "drain"]
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download waterway elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    name : str, optional
        The name of the file to store waterway geometries, by default "waterways.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes rivers, canals, streams, brooks, ditches, and drains.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    final_waterways_gdf = load_waterways(aoi, source, query, crs)
    if not final_waterways_gdf.empty:
        storage.create(final_waterways_gdf, name=name)
