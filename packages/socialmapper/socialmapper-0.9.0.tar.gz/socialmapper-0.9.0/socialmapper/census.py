"""Simple, straightforward census data fetching for SocialMapper.

No over-engineering, just functions that do what you need.
"""

import logging
import os
from functools import lru_cache
from typing import Any

import geopandas as gpd
import pandas as pd
import requests

logger = logging.getLogger(__name__)


class CensusClient:
    """Simple client for fetching census data from the US Census API."""

    BASE_URL = "https://api.census.gov/data"

    def __init__(self, api_key: str | None = None):
        """Initialize census client with optional API key.

        Parameters
        ----------
        api_key : str or None, optional
            Census API key. If None, uses CENSUS_API_KEY environment
            variable.

        Notes:
        -----
        API keys can be obtained for free at:
        https://api.census.gov/data/key_signup.html
        """
        self.api_key = api_key or os.getenv("CENSUS_API_KEY")
        self.session = requests.Session()

    def get_data(
        self,
        variables: list[str],
        geographic_units: list[str],
        year: int = 2023,
        dataset: str = "acs/acs5"
    ) -> pd.DataFrame:
        """Fetch census data for specified variables and geographic units.

        Parameters
        ----------
        variables : list of str
            List of census variable codes (e.g., ["B01003_001E",
            "B19013_001E"]).
        geographic_units : list of str
            List of geographic unit IDs (block groups, tracts, etc.).
        year : int, optional
            Census year, by default 2023.
        dataset : str, optional
            Census dataset identifier, by default "acs/acs5" (5-year ACS).

        Returns:
        -------
        pd.DataFrame
            DataFrame with census data including requested variables
            and geographic identifiers. Returns empty DataFrame on error.

        Examples:
        --------
        >>> client = CensusClient()
        >>> data = client.get_data(
        ...     ["B01003_001E"],  # Total population
        ...     ["120010001001"]   # Block group ID
        ... )
        >>> print(data.columns.tolist())
        ['B01003_001E', 'state', 'county', 'tract', 'block group']
        """
        if not geographic_units:
            return pd.DataFrame()

        # Build API URL
        url = f"{self.BASE_URL}/{year}/{dataset}"

        # Prepare parameters
        params = {
            "get": ",".join(variables),
            "for": self._format_geography(geographic_units),
        }

        if self.api_key:
            params["key"] = self.api_key

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()
            if len(data) <= 1:  # Only header row or empty
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])

            # Convert numeric columns
            for var in variables:
                if var in df.columns:
                    df[var] = pd.to_numeric(df[var], errors='coerce')

            return df

        except Exception as e:
            logger.error(f"Census API error: {e}")
            return pd.DataFrame()

    def _format_geography(self, units: list[str]) -> str:
        """Format geographic units for API query."""
        if not units:
            return ""

        # Determine geography type based on ID length
        sample = units[0]

        if len(sample) == 12:  # Block group
            # Format: state (2) + county (3) + tract (6) + block group (1)
            return f"block group:{','.join(u[-1] for u in units)}&in=state:{sample[:2]}"
        elif len(sample) == 11:  # Census tract
            return f"tract:{','.join(u[-6:] for u in units)}&in=state:{sample[:2]}"
        elif len(sample) == 5:  # County
            return f"county:{','.join(u[-3:] for u in units)}&in=state:{sample[:2]}"
        elif len(sample) == 2:  # State
            return f"state:{','.join(units)}"
        else:  # ZCTA or other
            return f"zip code tabulation area:{','.join(units)}"


def get_census_data_for_polygon(
    polygon: gpd.GeoDataFrame,
    variables: list[str],
    api_key: str | None = None,
    year: int = 2023
) -> pd.DataFrame:
    """Get census data for all block groups within any polygon.

    General-purpose function that works with any polygon geometry,
    including isochrones, shapefiles, or GeoJSON boundaries.

    Parameters
    ----------
    polygon : gpd.GeoDataFrame
        GeoDataFrame containing polygon geometry from any source
        (isochrones, shapefiles, GeoJSON, etc.).
    variables : list of str
        List of census variables to fetch (e.g., ["B01003_001E"]).
    api_key : str or None, optional
        Census API key. If None, uses CENSUS_API_KEY environment variable.
    year : int, optional
        Census year for data retrieval, by default 2023.

    Returns:
    -------
    pd.DataFrame
        DataFrame with census data for all block groups intersecting
        the polygon, including geometries and requested variables.

    Notes:
    -----
    This function identifies all census block groups that intersect
    with the provided polygon and fetches the requested census data
    for those block groups.

    Examples:
    --------
    >>> # Works with isochrones
    >>> iso = create_isochrone(location, travel_time=15)
    >>> data = get_census_data_for_polygon(iso, ["B01003_001E"])
    >>> print(f"Found {len(data)} block groups")

    >>> # Also works with any polygon from GIS tools
    >>> study_area = gpd.read_file("study_area.shp")
    >>> data = get_census_data_for_polygon(study_area, ["B19013_001E"])
    """
    # Get block groups that intersect the polygon
    block_groups = get_block_groups_for_polygon(polygon)

    if block_groups.empty:
        logger.warning("No block groups found for polygon")
        return pd.DataFrame()

    # Extract block group GEOIDs
    geoids = block_groups['GEOID'].tolist()

    # Fetch census data
    client = CensusClient(api_key)
    census_data = client.get_data(variables, geoids, year=year)

    # Merge with block group geometries if needed
    if not census_data.empty and 'GEOID' in census_data.columns:
        census_data = block_groups.merge(census_data, on='GEOID', how='left')

    return census_data




def get_block_groups_for_polygon(polygon: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Get census block groups that intersect with a polygon.
    
    Args:
        polygon: GeoDataFrame with polygon geometry
        
    Returns:
        GeoDataFrame of block groups that intersect the polygon
    """
    # Extract state and county from polygon bounds
    states_counties = identify_states_counties(polygon)

    if not states_counties:
        logger.warning("Could not identify states/counties for polygon")
        return gpd.GeoDataFrame()

    # Fetch block groups for identified counties
    all_block_groups = []

    for state_fips, county_fips in states_counties:
        bg = fetch_block_groups(state_fips, county_fips)
        if not bg.empty:
            all_block_groups.append(bg)

    if not all_block_groups:
        return gpd.GeoDataFrame()

    # Combine all block groups
    block_groups = pd.concat(all_block_groups, ignore_index=True)

    # Ensure same CRS
    if polygon.crs != block_groups.crs:
        block_groups = block_groups.to_crs(polygon.crs)

    # Find intersecting block groups
    intersecting = block_groups[block_groups.intersects(polygon.unary_union)]

    return intersecting


def identify_states_counties(polygon: gpd.GeoDataFrame) -> list[tuple[str, str]]:
    """Identify state and county FIPS codes for a polygon area.
    
    Args:
        polygon: GeoDataFrame with polygon geometry
        
    Returns:
        List of (state_fips, county_fips) tuples
    """
    # Get polygon centroid for geocoding
    # Ensure we're in WGS84 (EPSG:4326) for lat/lon coordinates
    if polygon.crs and polygon.crs != 'EPSG:4326':
        polygon_wgs84 = polygon.to_crs('EPSG:4326')
        centroid = polygon_wgs84.geometry.centroid.iloc[0]
    else:
        centroid = polygon.geometry.centroid.iloc[0]
    lat, lon = centroid.y, centroid.x

    # Use census geocoder to identify location
    geo_info = geocode_point(lat, lon)

    if geo_info and 'state_fips' in geo_info and 'county_fips' in geo_info:
        # Start with the main county
        counties = [(geo_info['state_fips'], geo_info['county_fips'])]

        # Could add neighboring counties for polygons that span multiple counties
        # For now, just return the main county
        return counties

    return []


def geocode_point(lat: float, lon: float) -> dict[str, str] | None:
    """Get geographic identifiers for a lat/lon point using Census geocoder.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dict with state_fips, county_fips, tract, block_group
    """
    url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"

    params = {
        'x': lon,
        'y': lat,
        'benchmark': 'Public_AR_Current',
        'vintage': 'Current_Current',
        'format': 'json'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('result') and data['result'].get('geographies'):
            # Extract from Census Blocks (most detailed)
            blocks = data['result']['geographies'].get('Census Blocks', [])
            if blocks and len(blocks) > 0:
                block = blocks[0]
                return {
                    'state_fips': block.get('STATE'),
                    'county_fips': block.get('COUNTY'),
                    'tract': block.get('TRACT'),
                    'block_group': block.get('BLKGRP')
                }

    except Exception as e:
        logger.error(f"Geocoding error for ({lat}, {lon}): {e}")

    return None


@lru_cache(maxsize=100)
def fetch_block_groups(state_fips: str, county_fips: str, year: int = 2023) -> gpd.GeoDataFrame:
    """Fetch block group boundaries from Census TIGER/Line files.
    
    Args:
        state_fips: 2-digit state FIPS code
        county_fips: 3-digit county FIPS code
        year: Census year
        
    Returns:
        GeoDataFrame with block group boundaries
    """
    # Build URL for TIGER/Line shapefile
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/BG/tl_{year}_{state_fips}_bg.zip"

    try:
        # Read directly from URL
        gdf = gpd.read_file(url)

        # Filter to specific county
        gdf = gdf[gdf['COUNTYFP'] == county_fips].copy()

        # Create full GEOID
        gdf['GEOID'] = gdf['STATEFP'] + gdf['COUNTYFP'] + gdf['TRACTCE'] + gdf['BLKGRPCE']

        return gdf[['GEOID', 'geometry']]

    except Exception as e:
        logger.error(f"Error fetching block groups for {state_fips}-{county_fips}: {e}")
        return gpd.GeoDataFrame()


# Simple variable name mapping
VARIABLE_MAPPING = {
    'total_population': 'B01003_001E',
    'median_household_income': 'B19013_001E',
    'median_age': 'B01002_001E',
    'total_housing_units': 'B25001_001E',
    'occupied_housing_units': 'B25003_001E',
    'owner_occupied': 'B25003_002E',
    'renter_occupied': 'B25003_003E',
    'white_population': 'B02001_002E',
    'black_population': 'B02001_003E',
    'asian_population': 'B02001_005E',
    'hispanic_population': 'B03002_012E',
    'poverty_population': 'B17001_002E',
    'education_bachelors_plus': 'B15003_022E',
    'education_high_school_plus': 'B15003_017E',
    'households_with_vehicle': 'B08201_002E',
    'households_no_vehicle': 'B08201_002E',
    'median_home_value': 'B25077_001E',
    'median_rent': 'B25064_001E',
}


def normalize_variables(variables: list[str]) -> list[str]:
    """Convert human-readable variable names to census codes.
    
    Args:
        variables: List of variable names (can be codes or readable names)
        
    Returns:
        List of census variable codes
    """
    normalized = []

    for var in variables:
        # If it's already a code (starts with letter, has underscore)
        if '_' in var and var[0].isalpha() and var[0].isupper():
            normalized.append(var)
        # Otherwise try to map it
        elif var.lower() in VARIABLE_MAPPING:
            normalized.append(VARIABLE_MAPPING[var.lower()])
        else:
            # If not found, keep original (might be valid but unknown)
            logger.warning(f"Unknown variable: {var}, keeping as-is")
            normalized.append(var)

    return normalized


def get_census_data(
    location: Any,
    variables: list[str],
    api_key: str | None = None,
    year: int = 2023
) -> pd.DataFrame:
    """Flexible census data fetching for various input types.
    
    Args:
        location: Can be:
            - GeoDataFrame with polygon (isochrone)
            - List of GEOID strings
            - Tuple of (lat, lon)
            - Dict with 'state_fips' and 'county_fips'
        variables: List of census variables (names or codes)
        api_key: Census API key
        year: Census year
        
    Returns:
        DataFrame with census data
    """
    # Normalize variables
    variables = normalize_variables(variables)

    # Handle different location types
    if isinstance(location, gpd.GeoDataFrame):
        # Isochrone or polygon
        return get_census_data_for_polygon(location, variables, api_key, year)

    elif isinstance(location, list):
        # List of GEOIDs
        client = CensusClient(api_key)
        return client.get_data(variables, location, year)

    elif isinstance(location, tuple) and len(location) == 2:
        # (lat, lon) point
        geo_info = geocode_point(location[0], location[1])
        if geo_info:
            # Get block group GEOID
            geoid = (geo_info['state_fips'] + geo_info['county_fips'] +
                    geo_info['tract'] + geo_info['block_group'])
            client = CensusClient(api_key)
            return client.get_data(variables, [geoid], year)

    elif isinstance(location, dict) and 'state_fips' in location:
        # State/county dict
        block_groups = fetch_block_groups(
            location['state_fips'],
            location.get('county_fips', '001')
        )
        if not block_groups.empty:
            client = CensusClient(api_key)
            return client.get_data(variables, block_groups['GEOID'].tolist(), year)

    logger.error(f"Unsupported location type: {type(location)}")
    return pd.DataFrame()


# Convenience functions for common use cases
def get_demographics_for_polygon(
    polygon: gpd.GeoDataFrame,
    api_key: str | None = None
) -> dict[str, Any]:
    """Get common demographic statistics for any polygon area.
    
    Works with any polygon geometry - isochrones, custom study areas,
    administrative boundaries, or polygons from GIS tools.
    
    Args:
        polygon: GeoDataFrame with polygon geometry (any source)
        api_key: Census API key
        
    Returns:
        Dict with demographic summary statistics
        
    Example:
        # With isochrone
        iso = create_isochrone(location, travel_time=15)
        demographics = get_demographics_for_polygon(iso)
        
        # With custom polygon
        study_area = gpd.read_file("my_area.geojson")
        demographics = get_demographics_for_polygon(study_area)
    """
    # Common demographic variables
    variables = [
        'total_population',
        'median_household_income',
        'median_age',
        'poverty_population',
        'households_no_vehicle'
    ]

    # Get census data
    data = get_census_data(polygon, variables, api_key)

    if data.empty:
        return {}

    # Calculate summary statistics
    stats = {}

    for var in variables:
        code = normalize_variables([var])[0]
        if code in data.columns:
            values = data[code].dropna()
            if not values.empty:
                if 'median' in var:
                    stats[var] = values.median()
                else:
                    stats[var] = values.sum()

    return stats
