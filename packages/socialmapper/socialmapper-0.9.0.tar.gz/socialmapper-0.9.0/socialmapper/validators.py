"""Input validation for SocialMapper API functions."""

from .constants import (
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MAX_TRAVEL_TIME,
    MIN_LATITUDE,
    MIN_LONGITUDE,
    MIN_TRAVEL_TIME,
    VALID_EXPORT_FORMATS,
    VALID_REPORT_FORMATS,
    VALID_TRAVEL_MODES,
)


class InputValidationError(Exception):
    """Exception raised when input validation fails."""


def _validate_coordinates_strict(lat: str | int | float, lon: str | int | float) -> tuple[float, float]:
    """Validate coordinate values (raises exception on invalid).

    Args:
        lat: Latitude value
        lon: Longitude value

    Returns:
        Tuple of validated (latitude, longitude) as floats

    Raises:
        InputValidationError: If coordinates are invalid
    """
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError) as e:
        raise InputValidationError(f"Coordinates must be numeric: {e}") from None

    # Validate ranges
    if not MIN_LATITUDE <= lat <= MAX_LATITUDE:
        raise InputValidationError(f"Invalid latitude: {lat}. Must be between -90 and 90")

    if not MIN_LONGITUDE <= lon <= MAX_LONGITUDE:
        raise InputValidationError(f"Invalid longitude: {lon}. Must be between -180 and 180")

    return lat, lon


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude coordinates.

    Parameters
    ----------
    lat : float
        Latitude value to validate.
    lon : float
        Longitude value to validate.

    Returns:
    -------
    bool
        True if coordinates are valid, False otherwise.
    """
    try:
        _validate_coordinates_strict(lat, lon)
        return True
    except InputValidationError:
        return False


def validate_travel_time(travel_time: int) -> None:
    """Validate travel time parameter.

    Parameters
    ----------
    travel_time : int
        Travel time in minutes to validate.

    Raises:
    ------
    ValueError
        If travel time is outside valid range.
    """
    if not MIN_TRAVEL_TIME <= travel_time <= MAX_TRAVEL_TIME:
        raise ValueError(
            f"Travel time must be between {MIN_TRAVEL_TIME} and {MAX_TRAVEL_TIME} minutes, "
            f"got {travel_time}"
        )


def validate_travel_mode(travel_mode: str) -> None:
    """Validate travel mode parameter.

    Parameters
    ----------
    travel_mode : str
        Travel mode to validate.

    Raises:
    ------
    ValueError
        If travel mode is not supported.
    """
    if travel_mode not in VALID_TRAVEL_MODES:
        raise ValueError(
            f"Travel mode must be one of {VALID_TRAVEL_MODES}, "
            f"got '{travel_mode}'"
        )


def validate_export_format(export_format: str) -> None:
    """Validate map export format.

    Parameters
    ----------
    export_format : str
        Export format to validate.

    Raises:
    ------
    ValueError
        If export format is not supported.
    """
    if export_format not in VALID_EXPORT_FORMATS:
        raise ValueError(
            f"Export format must be one of {VALID_EXPORT_FORMATS}, "
            f"got '{export_format}'"
        )


def validate_report_format(report_format: str) -> None:
    """Validate report format.

    Parameters
    ----------
    report_format : str
        Report format to validate.

    Raises:
    ------
    ValueError
        If report format is not supported.
    """
    if report_format not in VALID_REPORT_FORMATS:
        raise ValueError(
            f"Report format must be one of {VALID_REPORT_FORMATS}, "
            f"got '{report_format}'"
        )


def validate_location_input(
    polygon=None,
    location=None
) -> None:
    """Validate mutually exclusive location parameters.

    Ensures exactly one of polygon or location is provided,
    preventing ambiguous input specifications.

    Parameters
    ----------
    polygon : dict, optional
        GeoJSON polygon specification. Default is None.
    location : tuple, optional
        Coordinate tuple specification. Default is None.

    Raises:
    ------
    ValueError
        If neither parameter is provided or both are provided.

    Examples:
    --------
    >>> validate_location_input(polygon={"type": "Polygon"})
    >>> # No exception raised

    >>> validate_location_input()  # doctest: +SKIP
    ValueError: Must provide either polygon or location
    """
    if polygon is None and location is None:
        raise ValueError("Must provide either polygon or location")

    if polygon is not None and location is not None:
        raise ValueError("Provide either polygon or location, not both")
