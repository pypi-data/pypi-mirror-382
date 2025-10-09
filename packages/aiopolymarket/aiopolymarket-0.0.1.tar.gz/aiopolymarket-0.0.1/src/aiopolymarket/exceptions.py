"""
Custom exceptions for the Polymarket Gamma API client.
"""


class PolymarketAPIError(Exception):
    """Base exception for all Polymarket API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MarketNotFoundError(PolymarketAPIError):
    """Raised when a market is not found (404)."""

    def __init__(self, market_id: str):
        super().__init__(f"Market not found: {market_id}", status_code=404)
        self.market_id = market_id


class EventNotFoundError(PolymarketAPIError):
    """Raised when an event is not found (404)."""

    def __init__(self, event_id: str):
        super().__init__(f"Event not found: {event_id}", status_code=404)
        self.event_id = event_id


class RateLimitError(PolymarketAPIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ValidationError(PolymarketAPIError):
    """Raised when response validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}")


class NetworkError(PolymarketAPIError):
    """Raised when a network error occurs."""

    def __init__(self, message: str):
        super().__init__(f"Network error: {message}")
