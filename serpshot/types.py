"""Type definitions and enumerations for SerpShot SDK."""

from enum import Enum
from typing import Any, TypeAlias

__all__ = ["SearchType", "Device", "LocationType", "Headers", "QueryParams"]


class SearchType(str, Enum):
    """Search type enumeration."""

    SEARCH = "search"
    IMAGE = "image"


class Device(str, Enum):
    """Device type for search simulation."""

    DESKTOP = "desktop"
    MOBILE = "mobile"


class LocationType(str, Enum):
    """Google search location type enumeration.

    Matches backend GoogleSearchLocationType enum values.
    """

    US = "US"
    IN = "IN"
    JP = "JP"
    BR = "BR"
    GB = "GB"
    DE = "DE"
    CA = "CA"
    FR = "FR"
    ID = "ID"
    MX = "MX"
    SG = "SG"
    IR = "IR"


# Type aliases
Headers: TypeAlias = dict[str, str]
QueryParams: TypeAlias = dict[str, Any]
