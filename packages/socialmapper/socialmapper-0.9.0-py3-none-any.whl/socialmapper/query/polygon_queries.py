#!/usr/bin/env python3
"""Polygon-based POI discovery queries for Overpass API.

This module provides functionality to query POIs within polygon boundaries
using the Overpass API, with support for isochrone geometries and category
filtering based on the POI categorization system.
"""

import logging
from typing import Any

import overpy
from shapely.geometry import MultiPolygon, Polygon

from ..poi_categorization import (
    POI_CATEGORY_MAPPING,
    get_category_values,
    is_valid_category,
)

logger = logging.getLogger(__name__)

# Default timeout for Overpass API queries (in seconds)
DEFAULT_OVERPASS_TIMEOUT = 180

# Maximum number of coordinate pairs per polygon query (Overpass API limit)
MAX_POLYGON_COORDINATES = 3000

# Coordinate precision for Overpass API (decimal places)
COORDINATE_PRECISION = 7


def _format_coordinate(value: float, precision: int = COORDINATE_PRECISION) -> str:
    """Format a coordinate value with specified precision.

    Args:
        value: Coordinate value (latitude or longitude)
        precision: Number of decimal places

    Returns:
        Formatted coordinate string
    """
    return f"{value:.{precision}f}"


def _polygon_to_overpass_format(polygon: Polygon) -> str:
    """Convert a Shapely Polygon to Overpass API polygon format.

    Args:
        polygon: Shapely Polygon object

    Returns:
        Space-separated string of lat/lon pairs

    Raises:
        ValueError: If polygon has too many coordinates
    """
    # Get exterior coordinates (excluding the closing coordinate)
    coords = list(polygon.exterior.coords[:-1])

    if len(coords) > MAX_POLYGON_COORDINATES:
        raise ValueError(
            f"Polygon has {len(coords)} coordinates, exceeding Overpass API limit "
            f"of {MAX_POLYGON_COORDINATES}. Consider simplifying the polygon."
        )

    # Format as "lat1 lon1 lat2 lon2 ..."
    coord_pairs = []
    for lon, lat in coords:  # Shapely uses (lon, lat) order
        coord_pairs.extend([_format_coordinate(lat), _format_coordinate(lon)])

    return " ".join(coord_pairs)


def _multipolygon_to_overpass_queries(multipolygon: MultiPolygon) -> list[str]:
    """Convert a MultiPolygon to multiple Overpass polygon queries.

    Args:
        multipolygon: Shapely MultiPolygon object

    Returns:
        List of polygon format strings, one for each polygon
    """
    polygon_strings = []

    for polygon in multipolygon.geoms:
        try:
            polygon_str = _polygon_to_overpass_format(polygon)
            polygon_strings.append(polygon_str)
        except ValueError as e:
            logger.warning(f"Skipping polygon in multipolygon: {e}")
            continue

    return polygon_strings


def _build_category_tag_filters(categories: list[str] | None = None) -> list[dict[str, str]]:
    """Build tag filters for specified POI categories.

    Args:
        categories: List of category names from POI_CATEGORY_MAPPING.
                   If None, includes all categories.

    Returns:
        List of tag filter dictionaries
    """
    tag_filters = []

    # If no categories specified, use all
    if categories is None:
        categories = list(POI_CATEGORY_MAPPING.keys())

    # Validate categories
    invalid_categories = [cat for cat in categories if not is_valid_category(cat)]
    if invalid_categories:
        logger.warning(f"Invalid categories will be ignored: {invalid_categories}")
        categories = [cat for cat in categories if is_valid_category(cat)]

    # Build tag filters based on OSM key priority
    osm_key_to_values: dict[str, list[str]] = {}

    for category in categories:
        values = get_category_values(category)
        if not values:
            continue

        # Group values by their likely OSM key
        for value in values:
            # Determine the OSM key based on the value and category
            osm_key = _infer_osm_key(value, category)
            if osm_key not in osm_key_to_values:
                osm_key_to_values[osm_key] = []
            osm_key_to_values[osm_key].append(value)

    # Create tag filters
    for osm_key, values in osm_key_to_values.items():
        for value in values:
            tag_filters.append({osm_key: value})

    return tag_filters


# OSM key mappings for POI categories
_OSM_KEY_MAPPINGS = {
    "food_and_drink": {
        "amenity": {
            "restaurant", "cafe", "bar", "fast_food", "pub",
            "food_court", "ice_cream", "biergarten", "nightclub"
        },
        "shop": "*"  # Default for food_and_drink category
    },
    "shopping": {
        "amenity": {"shop", "marketplace"},
        "shop": "*"  # Default for shopping category
    },
    "education": {
        "amenity": "*"  # All education values go to amenity
    },
    "healthcare": {
        "amenity": {"pharmacy"},
        "healthcare": "*"  # Default for healthcare category
    },
    "transportation": {
        "amenity": {"fuel", "charging_station", "parking", "taxi"},
        "railway": {"bus_station", "train_station"},
        "public_transport": "*"  # Default for transportation category
    },
    "recreation": {
        "amenity": {"cinema", "theatre"},
        "leisure": "*"  # Default for recreation category
    },
    "services": {
        "amenity": {"bank", "atm", "post_office", "police", "fire_station"},
        "office": "*"  # Default for services category
    },
    "accommodation": {
        "tourism": "*"  # All accommodation values go to tourism
    },
    "religious": {
        "amenity": {"place_of_worship"},
        "building": "*"  # Default for religious category
    },
    "utilities": {
        "amenity": "*"  # All utilities values go to amenity
    }
}


def _infer_osm_key(value: str, category: str) -> str:
    """Infer the OSM key for a given value based on category context.

    Args:
        value: The OSM tag value
        category: The POI category

    Returns:
        The inferred OSM key (e.g., 'amenity', 'shop', 'leisure')
    """
    category_mapping = _OSM_KEY_MAPPINGS.get(category, {})

    # Check each OSM key in the category mapping
    for osm_key, values in category_mapping.items():
        if values == "*" or value in values:
            return osm_key

    # Default fallback if no category match
    return "amenity"


def build_poi_discovery_query(
    geometry: Polygon | MultiPolygon,
    categories: list[str] | None = None,
    timeout: int = DEFAULT_OVERPASS_TIMEOUT,
    additional_tags: dict[str, str] | None = None,
) -> str:
    """Build an Overpass API query for POI discovery within a polygon.

    Args:
        geometry: Shapely Polygon or MultiPolygon defining the search area
        categories: Optional list of POI categories to filter by
        timeout: Query timeout in seconds
        additional_tags: Optional additional OSM tags to filter by

    Returns:
        Complete Overpass API query string

    Raises:
        ValueError: If geometry is not a Polygon or MultiPolygon
    """
    if not isinstance(geometry, Polygon | MultiPolygon):
        raise ValueError(
            f"Geometry must be a Polygon or MultiPolygon, got {type(geometry).__name__}"
        )

    # Start query with JSON output and timeout
    query_parts = [f"[out:json][timeout:{timeout}];", "("]

    # Get polygon strings
    if isinstance(geometry, Polygon):
        polygon_strings = [_polygon_to_overpass_format(geometry)]
    else:
        polygon_strings = _multipolygon_to_overpass_queries(geometry)

    if not polygon_strings:
        raise ValueError("No valid polygons found in geometry")

    # Build tag filters
    tag_filters = _build_category_tag_filters(categories)

    # Add additional tags if provided
    if additional_tags:
        for key, value in additional_tags.items():
            tag_filters.append({key: value})

    # If no filters specified, query all POIs
    if not tag_filters:
        tag_filters = [{}]  # Empty filter matches all

    # Build query parts for each polygon and tag combination
    for polygon_str in polygon_strings:
        for tag_filter in tag_filters:
            # Build tag filter string
            tag_str = ""
            for key, value in tag_filter.items():
                tag_str += f'["{key}"="{value}"]'

            # Add query for nodes, ways, and relations
            query_parts.append(f'  node{tag_str}(poly:"{polygon_str}");')
            query_parts.append(f'  way{tag_str}(poly:"{polygon_str}");')
            query_parts.append(f'  relation{tag_str}(poly:"{polygon_str}");')

    # Close union and add output statement
    query_parts.extend([");", "out center;"])

    return "\n".join(query_parts)


def _query_overpass_with_polygon(query: str) -> overpy.Result:
    """Execute an Overpass API query with simple retry logic.

    Args:
        query: The Overpass API query string

    Returns:
        Query result from overpy

    Raises:
        Exception: If query fails after retries
    """
    import time

    api = overpy.Overpass(url="https://overpass-api.de/api/interpreter")
    max_retries = 3
    base_delay = 2.0

    for attempt in range(max_retries):
        try:
            logger.debug(f"Sending polygon query to Overpass API (length: {len(query)} chars)")
            return api.query(query)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Error querying Overpass API after {max_retries} attempts: {e}")
                logger.debug(f"Query excerpt: {query[:500]}...")  # Log first 500 chars
                raise
            else:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Overpass API query failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s: {e}")
                time.sleep(delay)


def query_pois_in_polygon(
    geometry: Polygon | MultiPolygon,
    categories: list[str] | None = None,
    timeout: int = DEFAULT_OVERPASS_TIMEOUT,
    additional_tags: dict[str, str] | None = None,
    simplify_tolerance: float | None = None,
) -> dict[str, Any]:
    """Query POIs within a polygon boundary using Overpass API.

    This function builds and executes an Overpass API query to find POIs
    within the specified polygon geometry, with optional category filtering.

    Args:
        geometry: Shapely Polygon or MultiPolygon defining the search area
        categories: Optional list of POI categories to filter by (from POI_CATEGORY_MAPPING)
        timeout: Query timeout in seconds (default: 180)
        additional_tags: Optional additional OSM tags to filter by
        simplify_tolerance: Optional tolerance for simplifying the geometry before querying

    Returns:
        Dictionary containing:
            - poi_count: Total number of POIs found
            - pois: List of POI dictionaries with id, type, lat, lon, tags
            - query_info: Metadata about the query (geometry area, categories, etc.)

    Raises:
        ValueError: If geometry is invalid or too complex
        Exception: If Overpass API query fails

    Example:
        >>> from shapely.geometry import Polygon
        >>> # Create a simple square polygon
        >>> polygon = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        >>> # Query restaurants and cafes within the polygon
        >>> result = query_pois_in_polygon(polygon, categories=["food_and_drink"])
        >>> print(f"Found {result['poi_count']} POIs")
    """
    # Validate and potentially simplify geometry
    if not geometry.is_valid:
        logger.warning("Invalid geometry detected, attempting to fix")
        geometry = geometry.buffer(0)  # Common fix for invalid geometries

    if simplify_tolerance:
        original_area = geometry.area
        geometry = geometry.simplify(simplify_tolerance, preserve_topology=True)
        logger.info(f"Simplified geometry from area {original_area:.6f} to {geometry.area:.6f}")

    # Build the query
    query = build_poi_discovery_query(
        geometry=geometry,
        categories=categories,
        timeout=timeout,
        additional_tags=additional_tags,
    )

    # Log query info
    logger.info(f"Querying POIs in polygon with area: {geometry.area:.6f}")
    if categories:
        logger.info(f"Filtering by categories: {categories}")

    # Execute query
    result = _query_overpass_with_polygon(query)

    # Format results
    pois = []

    # Process nodes
    for node in result.nodes:
        poi_data = {
            "id": node.id,
            "type": "node",
            "lat": float(node.lat),
            "lon": float(node.lon),
            "tags": dict(node.tags),
        }
        pois.append(poi_data)

    # Process ways (with center coordinates)
    for way in result.ways:
        center_lat = getattr(way, "center_lat", None)
        center_lon = getattr(way, "center_lon", None)

        if center_lat and center_lon:
            poi_data = {
                "id": way.id,
                "type": "way",
                "lat": float(center_lat),
                "lon": float(center_lon),
                "tags": dict(way.tags),
            }
            pois.append(poi_data)

    # Process relations (with center coordinates)
    for relation in result.relations:
        center_lat = getattr(relation, "center_lat", None)
        center_lon = getattr(relation, "center_lon", None)

        if center_lat and center_lon:
            poi_data = {
                "id": relation.id,
                "type": "relation",
                "lat": float(center_lat),
                "lon": float(center_lon),
                "tags": dict(relation.tags),
            }
            pois.append(poi_data)

    # Build response
    response = {
        "poi_count": len(pois),
        "pois": pois,
        "query_info": {
            "geometry_type": type(geometry).__name__,
            "geometry_area": geometry.area,
            "categories": categories or "all",
            "additional_tags": additional_tags,
            "timeout": timeout,
        },
    }

    logger.info(f"Found {len(pois)} POIs in polygon")

    return response


def query_pois_from_isochrone(
    isochrone_gdf,
    categories: list[str] | None = None,
    timeout: int = DEFAULT_OVERPASS_TIMEOUT,
    additional_tags: dict[str, str] | None = None,
    simplify_tolerance: float | None = 0.001,
) -> dict[str, Any]:
    """Query POIs within an isochrone boundary.

    This is a convenience function that extracts the geometry from an
    isochrone GeoDataFrame and queries POIs within it.

    Args:
        isochrone_gdf: GeoDataFrame containing isochrone geometry
        categories: Optional list of POI categories to filter by
        timeout: Query timeout in seconds
        additional_tags: Optional additional OSM tags to filter by
        simplify_tolerance: Tolerance for simplifying the geometry (default: 0.001)

    Returns:
        Dictionary containing POI results

    Raises:
        ValueError: If isochrone_gdf is invalid or empty
    """
    if isochrone_gdf is None or isochrone_gdf.empty:
        raise ValueError("Isochrone GeoDataFrame is empty or None")

    # Extract geometry (should be a single polygon or multipolygon)
    if len(isochrone_gdf) > 1:
        logger.warning(f"Isochrone contains {len(isochrone_gdf)} geometries, using union")
        geometry = isochrone_gdf.unary_union
    else:
        geometry = isochrone_gdf.geometry.iloc[0]

    # Ensure we have a Polygon or MultiPolygon
    if not isinstance(geometry, Polygon | MultiPolygon):
        raise ValueError(
            f"Isochrone geometry must be Polygon or MultiPolygon, got {type(geometry).__name__}"
        )

    # Query POIs
    return query_pois_in_polygon(
        geometry=geometry,
        categories=categories,
        timeout=timeout,
        additional_tags=additional_tags,
        simplify_tolerance=simplify_tolerance,
    )
