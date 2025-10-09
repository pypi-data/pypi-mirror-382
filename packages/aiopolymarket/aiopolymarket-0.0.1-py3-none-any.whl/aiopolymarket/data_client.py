"""
Async client for the Polymarket Data API.

This module provides a client for interacting with Polymarket's Data API
for positions, trades, activity, and holder information.
"""

import asyncio
from typing import Any

import aiohttp
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    NetworkError,
    PolymarketAPIError,
    RateLimitError,
    ValidationError,
)
from .models import Activity, Holder, Position, Trade


class DataClient:
    """
    Async client for Polymarket's Data API.

    This client provides methods for fetching user positions, trades,
    on-chain activity, and market holder information.

    Example:
        ```python
        async with DataClient() as client:
            positions = await client.get_positions(user="0x123...")
            for position in positions:
                print(f"{position.market}: {position.size}")
        ```
    """

    BASE_URL = "https://data-api.polymarket.com"
    POSITIONS_ENDPOINT = "/positions"
    TRADES_ENDPOINT = "/trades"
    ACTIVITY_ENDPOINT = "/activity"
    HOLDERS_ENDPOINT = "/holders"
    VALUE_ENDPOINT = "/value"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the Data API client.

        Args:
            base_url: Base URL for the API (defaults to production URL)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Initial delay between retries in seconds (exponential backoff)
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "DataClient":
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Make an HTTP request with retry logic and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            PolymarketAPIError: For various API errors
            NetworkError: For network-related errors
            RateLimitError: When rate limit is exceeded
        """
        await self._ensure_session()
        assert self._session is not None

        url = f"{self.base_url}{endpoint}"
        last_exception: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                async with self._session.request(method, url, params=params) as response:
                    # Handle rate limiting
                    if response.status == 429:
                        raise RateLimitError()

                    # Handle not found
                    if response.status == 404:
                        raise PolymarketAPIError("Resource not found", status_code=404)

                    # Handle other HTTP errors
                    if response.status >= 400:
                        text = await response.text()
                        raise PolymarketAPIError(
                            f"HTTP {response.status}: {text}",
                            status_code=response.status,
                        )

                    # Parse JSON response
                    try:
                        return await response.json()
                    except aiohttp.ContentTypeError as e:
                        raise PolymarketAPIError(f"Invalid JSON response: {e}")

            except aiohttp.ClientError as e:
                last_exception = NetworkError(str(e))
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)
                    await asyncio.sleep(delay)
                    continue
                raise last_exception

            except (RateLimitError, PolymarketAPIError):
                # Don't retry these
                raise

        # If we exhausted retries
        if last_exception:
            raise last_exception
        raise NetworkError("Request failed after retries")

    async def get_positions(
        self,
        user: str,
        *,
        market: str | None = None,
        size_threshold: float | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
    ) -> list[Position]:
        """
        Get positions for a user.

        Args:
            user: User address (required)
            market: Market condition ID to filter by
            size_threshold: Minimum position size
            limit: Maximum number of positions to return
            sort_by: Sorting criteria (e.g., "TOKENS", "CURRENT", "INITIAL")

        Returns:
            List of Position objects

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with DataClient() as client:
                positions = await client.get_positions(
                    user="0x123...",
                    size_threshold=100
                )
            ```
        """
        params: dict[str, Any] = {"user": user}
        if market is not None:
            params["market"] = market
        if size_threshold is not None:
            params["sizeThreshold"] = size_threshold
        if limit is not None:
            params["limit"] = limit
        if sort_by is not None:
            params["sortBy"] = sort_by

        data = await self._request("GET", self.POSITIONS_ENDPOINT, params=params)

        try:
            return [Position.model_validate(position) for position in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse positions: {e}")

    async def get_trades(
        self,
        *,
        user: str | None = None,
        market: str | None = None,
        taker_only: bool | None = None,
        filter_type: str | None = None,
        side: str | None = None,
        limit: int | None = None,
    ) -> list[Trade]:
        """
        Get trades for a user or market.

        Args:
            user: User address
            market: Market condition ID
            taker_only: Filter for taker orders only
            filter_type: Filter by "CASH" or "TOKENS"
            side: Trade side ("BUY" or "SELL")
            limit: Maximum number of trades to return

        Returns:
            List of Trade objects

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with DataClient() as client:
                trades = await client.get_trades(
                    user="0x123...",
                    side="BUY",
                    limit=50
                )
            ```
        """
        params: dict[str, Any] = {}
        if user is not None:
            params["user"] = user
        if market is not None:
            params["market"] = market
        if taker_only is not None:
            params["takerOnly"] = str(taker_only).lower()
        if filter_type is not None:
            params["filterType"] = filter_type
        if side is not None:
            params["side"] = side
        if limit is not None:
            params["limit"] = limit

        data = await self._request("GET", self.TRADES_ENDPOINT, params=params)

        try:
            return [Trade.model_validate(trade) for trade in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse trades: {e}")

    async def get_activity(
        self,
        user: str,
        *,
        market: str | None = None,
        activity_type: str | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> list[Activity]:
        """
        Get on-chain activity for a user.

        Args:
            user: User address (required)
            market: Market condition ID to filter by
            activity_type: Activity type ("TRADE", "SPLIT", "MERGE", etc.)
            start: Start timestamp
            end: End timestamp
            limit: Maximum number of activities to return

        Returns:
            List of Activity objects

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with DataClient() as client:
                activity = await client.get_activity(
                    user="0x123...",
                    activity_type="TRADE"
                )
            ```
        """
        params: dict[str, Any] = {"user": user}
        if market is not None:
            params["market"] = market
        if activity_type is not None:
            params["type"] = activity_type
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if limit is not None:
            params["limit"] = limit

        data = await self._request("GET", self.ACTIVITY_ENDPOINT, params=params)

        try:
            return [Activity.model_validate(activity) for activity in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse activity: {e}")

    async def get_holders(
        self,
        market: str,
        *,
        limit: int | None = None,
    ) -> list[Holder]:
        """
        Get top holders of a market.

        Args:
            market: Market condition ID (required)
            limit: Number of holders to return

        Returns:
            List of Holder objects

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with DataClient() as client:
                holders = await client.get_holders(
                    market="0xe3b423dfad8c22ff75c9899c4e8176f628cf4ad4caa00481764d320e7415f7a9",
                    limit=10
                )
            ```
        """
        params: dict[str, Any] = {"market": market}
        if limit is not None:
            params["limit"] = limit

        data = await self._request("GET", self.HOLDERS_ENDPOINT, params=params)

        try:
            return [Holder.model_validate(holder) for holder in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse holders: {e}")

    async def get_value(
        self,
        user: str,
        *,
        market: str | None = None,
    ) -> float:
        """
        Get total USD value of a user's positions.

        Args:
            user: User address (required)
            market: Optional market condition ID filter

        Returns:
            Total USD value as a float

        Raises:
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with DataClient() as client:
                value = await client.get_value(user="0x123...")
                print(f"Total portfolio value: ${value:,.2f}")
            ```
        """
        params: dict[str, Any] = {"user": user}
        if market is not None:
            params["market"] = market

        data = await self._request("GET", self.VALUE_ENDPOINT, params=params)

        # Value endpoint returns a single number or dict with value
        if isinstance(data, (int, float)):
            return float(data)
        if isinstance(data, dict) and "value" in data:
            return float(data["value"])
        raise ValidationError(f"Unexpected value response format: {data}")
