"""
Polymarket Gamma API Async Client

A high-quality, type-safe async client for Polymarket's Gamma Markets API.
"""

__version__ = "0.1.0"

from .client import GammaClient
from .data_client import DataClient
from .enums import MarketType, SeriesType, SortBy
from .exceptions import (
    EventNotFoundError,
    MarketNotFoundError,
    NetworkError,
    PolymarketAPIError,
    RateLimitError,
    ValidationError,
)
from .models import Activity, Event, Holder, Market, Position, Sampling, Series, Tag, Trade

__all__ = [
    # Clients
    "GammaClient",
    "DataClient",
    # Models
    "Market",
    "Event",
    "Series",
    "Tag",
    "Sampling",
    "Position",
    "Trade",
    "Activity",
    "Holder",
    # Enums
    "MarketType",
    "SeriesType",
    "SortBy",
    # Exceptions
    "PolymarketAPIError",
    "MarketNotFoundError",
    "EventNotFoundError",
    "RateLimitError",
    "ValidationError",
    "NetworkError",
]
