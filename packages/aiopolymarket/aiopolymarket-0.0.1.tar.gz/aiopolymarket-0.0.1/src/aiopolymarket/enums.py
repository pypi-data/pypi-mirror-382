"""
Enums and constants for the Polymarket Gamma API.
"""

from enum import Enum


class MarketType(str, Enum):
    """Market type enumeration."""

    NORMAL = "normal"
    SCALAR = "scalar"
    # Add other market types as discovered


class SortBy(str, Enum):
    """Sort order for events."""

    ASCENDING = "ascending"
    DESCENDING = "descending"
    PRICE = "price"


class SeriesType(str, Enum):
    """Series type enumeration."""

    # Add series types as discovered
    pass
