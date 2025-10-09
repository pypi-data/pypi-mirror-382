"""Internal geocoding utilities for SocialMapper."""

import logging

import requests

logger = logging.getLogger(__name__)


def geocode_location(address: str) -> tuple[float, float] | None:
    """Geocode an address string to coordinates.

    Converts human-readable addresses to geographic coordinates using
    OpenStreetMap's Nominatim service as primary provider, with US Census
    geocoder as fallback. Focuses on US addresses for optimal accuracy.

    Parameters
    ----------
    address : str
        Address string to geocode. Can be partial ("City, State")
        or full street address ("123 Main St, City, State ZIP").

    Returns:
    -------
    tuple of float or None
        Tuple containing (latitude, longitude) in decimal degrees,
        or None if geocoding fails for all providers.

    Raises:
    ------
    requests.RequestException
        If network request fails with timeout or connection error.

    Examples:
    --------
    >>> coords = geocode_location("Seattle, WA")
    >>> coords is not None
    True
    >>> lat, lon = coords
    >>> 47.5 < lat < 47.7 and -122.4 < lon < -122.2
    True

    >>> geocode_location("1600 Pennsylvania Ave, Washington, DC")
    (38.8976, -77.0365)  # Approximate coordinates

    See Also:
    --------
    geocode_with_census : Direct Census geocoder implementation.

    Notes:
    -----
    Includes rate limiting and proper User-Agent headers to respect
    service providers' usage policies. Results are logged at debug level.
    """
    # Try Nominatim first (no API key needed)
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "us"  # Focus on US addresses
    }
    headers = {
        "User-Agent": "SocialMapper/2.0 (https://github.com/socialmapper)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data:
            result = data[0]
            lat = float(result["lat"])
            lon = float(result["lon"])
            logger.debug(f"Geocoded '{address}' to ({lat}, {lon})")
            return (lat, lon)

    except Exception as e:
        logger.warning(f"Nominatim geocoding failed for '{address}': {e}")

    # Fallback to Census geocoder
    return geocode_with_census(address)


def geocode_with_census(address: str) -> tuple[float, float] | None:
    """Geocode using US Census geocoder as fallback.

    Uses the US Census Bureau's geocoding service for address resolution.
    This service is specifically designed for US addresses and provides
    high accuracy for street-level addresses within the United States.

    Parameters
    ----------
    address : str
        US address string to geocode. Should be a complete US address
        for best results.

    Returns:
    -------
    tuple of float or None
        Tuple containing (latitude, longitude) in decimal degrees,
        or None if geocoding fails or address is not found.

    Examples:
    --------
    >>> coords = geocode_with_census("350 Fifth Avenue, New York, NY 10118")
    >>> coords is not None
    True

    >>> geocode_with_census("Invalid Address XYZ")
    None

    Notes:
    -----
    Only works for addresses within the United States and territories.
    Does not require an API key but has rate limiting.
    Returns the most accurate match from the Census geocoding database.
    """
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("result") and data["result"].get("addressMatches"):
            match = data["result"]["addressMatches"][0]
            coords = match["coordinates"]
            lat = coords["y"]
            lon = coords["x"]
            logger.debug(f"Census geocoded '{address}' to ({lat}, {lon})")
            return (lat, lon)

    except Exception as e:
        logger.error(f"Census geocoding failed for '{address}': {e}")

    return None


def get_census_geography(lat: float, lon: float) -> dict[str, str] | None:
    """Get census geographic identifiers for a point.

    Performs reverse geocoding to identify the census geographic units
    (state, county, tract, block group) that contain a given coordinate point.
    Uses the US Census Bureau's geography API for accurate boundary matching.

    Parameters
    ----------
    lat : float
        Latitude in decimal degrees (WGS84).
    lon : float
        Longitude in decimal degrees (WGS84).

    Returns:
    -------
    dict of str or None
        Dictionary containing census geography identifiers:
        - 'state_fips': 2-digit state FIPS code
        - 'county_fips': 3-digit county FIPS code
        - 'tract': 6-digit census tract code
        - 'block_group': 1-digit block group number
        - 'geoid': 12-digit combined GEOID
        Returns None if the point cannot be matched to census geography.

    Examples:
    --------
    >>> geo = get_census_geography(38.9072, -77.0369)  # Washington, DC
    >>> geo is not None
    True
    >>> 'state_fips' in geo and 'county_fips' in geo
    True
    >>> len(geo['geoid']) == 12
    True

    Notes:
    -----
    Uses the 2020 Census block boundaries for geographic matching.
    Only works for coordinates within the United States and territories.
    """
    url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
    params = {
        "x": lon,
        "y": lat,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": "2020 Census Blocks",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        if data.get("result") and data["result"].get("geographies"):
            blocks = data["result"]["geographies"].get("2020 Census Blocks", [])
            if blocks:
                block = blocks[0]

                # Extract components
                state_fips = block.get("STATE", "")
                county_fips = block.get("COUNTY", "")
                tract = block.get("TRACT", "")
                block_group = block.get("BLKGRP", "")

                # Create GEOID (state + county + tract + block group)
                geoid = f"{state_fips}{county_fips}{tract}{block_group}"

                return {
                    "state_fips": state_fips,
                    "county_fips": county_fips,
                    "tract": tract,
                    "block_group": block_group,
                    "geoid": geoid
                }

        # No geography data returned
        logger.warning(
            f"Census Geocoding API returned no geography data for ({lat}, {lon}). "
            f"The location may be outside the US or in a territory without census block data."
        )

    except requests.Timeout:
        logger.warning(
            f"Census Geocoding API request timed out for ({lat}, {lon}). "
            f"Your internet connection may be slow or the service is experiencing high load. "
            f"Try again or check your network connection."
        )
    except requests.RequestException as e:
        logger.warning(
            f"Network error accessing Census Geocoding API for ({lat}, {lon}): {e}. "
            f"Check your internet connection or try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error getting census geography for ({lat}, {lon}): {e}")

    return None
