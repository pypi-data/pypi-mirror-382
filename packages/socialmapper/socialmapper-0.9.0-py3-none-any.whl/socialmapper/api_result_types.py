"""Result types for SocialMapper API operations.

This module provides Result, Ok, and Err types for functional error handling,
along with specific result types for POI discovery operations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')
E = TypeVar('E')


class Result(Generic[T, E]):
    """A Result type that can be either Ok or Err."""

    def __init__(self):
        raise NotImplementedError("Use Ok() or Err() to create Result instances")

    def is_ok(self) -> bool:
        """Check if this is an Ok result."""
        return isinstance(self, Ok)

    def is_err(self) -> bool:
        """Check if this is an Err result."""
        return isinstance(self, Err)

    def unwrap(self) -> T:
        """Get the value if Ok, raise if Err."""
        if isinstance(self, Ok):
            return self.value
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_err(self) -> E:
        """Get the error if Err, raise if Ok."""
        if isinstance(self, Err):
            return self.error
        raise ValueError(f"Called unwrap_err on Ok: {self.value}")


@dataclass
class Ok(Result[T, E]):
    """Successful result containing a value."""
    value: T

    def __init__(self, value: T):
        self.value = value


@dataclass
class Err(Result[T, E]):
    """Error result containing an error."""
    error: E

    def __init__(self, error: E):
        self.error = error


class ErrorType(str, Enum):
    """Types of errors that can occur in the API."""
    VALIDATION = "validation"
    API_ERROR = "api_error"
    NOT_FOUND = "not_found"
    NETWORK = "network"
    PARSING = "parsing"
    CONFIGURATION = "configuration"
    INTERNAL = "internal"


@dataclass
class Error:
    """Standard error information."""
    type: ErrorType
    message: str
    details: dict[str, Any] | None = None


class DiscoveredPOI(BaseModel):
    """Information about a discovered POI."""
    osm_id: int
    name: str | None = None
    category: str
    subcategory: str | None = None
    latitude: float
    longitude: float
    distance_meters: float
    travel_time_minutes: float | None = None
    tags: dict[str, Any] = Field(default_factory=dict)
    address: str | None = None


class NearbyPOIResult(BaseModel):
    """Result of nearby POI discovery."""
    origin: dict[str, float]  # {"latitude": ..., "longitude": ...}
    travel_time_minutes: int
    travel_mode: str
    discovered_pois: list[DiscoveredPOI]
    isochrone_area_sqkm: float | None = None
    categories_found: list[str] = Field(default_factory=list)
    total_pois: int = 0
    search_radius_meters: float | None = None


class NearbyPOIDiscoveryConfig(BaseModel):
    """Configuration for nearby POI discovery."""
    location: str | dict[str, float]  # Address or {"latitude": ..., "longitude": ...}
    travel_time: int = Field(ge=1, le=60)
    travel_mode: str = "drive"
    categories: list[str] | None = None
    max_results: int = 100
    include_details: bool = True
    output_format: str = "json"
    output_file: str | None = None
