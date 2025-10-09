from typing import Union, Optional, Dict, List, Any
import geopandas as gpd
import pandas as pd
import osmnx as ox
from shapely.validation import make_valid
from ..satellite.utils import create_aoi_geodataframe


def load_osm_data(
    aoi: Any,
    tags: Dict[str, List[str]],
    geometry_types: Optional[List[str]] = None,
    crs: str = "EPSG:4326",  # WGS84
) -> gpd.GeoDataFrame:
    """
    Load OSM data filtered by tags and geometry types.

    Parameters
    ----------
    area_of_interest : Union[str, gpd.GeoDataFrame]
        The area of interest
    tags : Dict[str, List[str]]
        The tags to filter the OSM data
    geometry_types : List[str], optional
        The geometry types to filter, by default None
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)

    Returns
    -------
    gpd.GeoDataFrame
        The filtered GeoDataFrame
    """
    gdf = create_aoi_geodataframe(aoi)

    osm_elements = get_all_osm_elements(gdf, tags)

    if not osm_elements:
        print("No elements found")
        return gpd.GeoDataFrame()

    combined_gdf = pd.concat(osm_elements, ignore_index=True)

    if geometry_types:
        combined_gdf = combined_gdf[combined_gdf.geometry.type.isin(geometry_types)]

    # Curate the combined GeoDataFrame
    combined_gdf = curate_osm_gdf(combined_gdf, crs)

    return combined_gdf


def get_all_osm_elements(
    aoi_gdf: gpd.GeoDataFrame, tags: Dict[str, Union[str, List[str]]]
) -> List[gpd.GeoDataFrame]:
    """
    Iterate over a given AOI GeoDataFrame and get all the desired OSM elements defined in the tags.

    Parameters
    ----------
    aoi_gdf: gpd.GeoDataFrame
        The GeoDataFrame of the Area of Interest
    tags: Dict[str, Union[str, List[str]]]
        Dict with the OSM tags of the elements to download

    Returns
    -------
    List[gpd.GeoDataFrame]
        List with all the required elements
    """
    osm_elements = []

    for _, row in aoi_gdf.iterrows():
        polygon = row.geometry
        if not polygon.is_valid:
            polygon = make_valid(polygon)

        for key, values in tags.items():
            if isinstance(values, list):
                for value in values:
                    try:
                        element_gdf = ox.features_from_polygon(
                            polygon, tags={key: value}
                        )
                        osm_elements.append(element_gdf)
                    except ox._errors.InsufficientResponseError:
                        continue
            else:
                try:
                    element_gdf = ox.features_from_polygon(polygon, tags={key: values})
                    osm_elements.append(element_gdf)
                except ox._errors.InsufficientResponseError:
                    continue

    return osm_elements


def curate_osm_gdf(gdf: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    """
    Curate the GeoDataFrame by converting timestamp and list columns to string,
    setting the index to osm_id, ensuring the correct CRS, and validating geometry.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame to be curated
    crs : str
        The coordinate reference system to use

    Returns
    -------
    gpd.GeoDataFrame
        The curated GeoDataFrame
    """
    # Ensure the GeoDataFrame has the correct CRS
    if gdf.crs is None:
        gdf.set_crs(crs, inplace=True)
    elif gdf.crs != crs:
        gdf = gdf.to_crs(crs)

    # Convert timestamp and list columns to string
    for column in gdf.columns:
        if column == "geometry":
            continue
        if pd.api.types.is_datetime64_any_dtype(
            gdf[column]
        ) or pd.api.types.is_list_like(gdf[column]):
            gdf[column] = gdf[column].astype(str)

    # Set the index to osm_id if it exists
    if "osmid" in gdf.columns:
        gdf.set_index("osmid", inplace=True)

    # Ensure geometry is valid
    gdf = gdf[gdf.geometry.notnull()]

    return gdf
