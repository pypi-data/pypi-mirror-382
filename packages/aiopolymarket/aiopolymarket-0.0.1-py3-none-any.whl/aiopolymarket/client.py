"""
Async client for the Polymarket Gamma API.

This module provides a high-quality, type-safe async client for interacting
with Polymarket's Gamma Markets API.
"""

import asyncio
from typing import Any, AsyncIterator
from urllib.parse import urljoin

import aiohttp
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    EventNotFoundError,
    MarketNotFoundError,
    NetworkError,
    PolymarketAPIError,
    RateLimitError,
    ValidationError,
)
from .models import Event, Market, Sampling, Tag


class GammaClient:
    """
    Async client for Polymarket's Gamma API.

    This client provides type-safe, async methods for fetching market and event data
    from Polymarket's Gamma API.

    Example:
        ```python
        async with GammaClient() as client:
            markets = await client.get_markets(active=True, limit=10)
            for market in markets:
                print(f"{market.question}: {market.volume_num}")
        ```
    """

    BASE_URL = "https://gamma-api.polymarket.com"
    MARKETS_ENDPOINT = "/markets"
    EVENTS_ENDPOINT = "/events"
    TAGS_ENDPOINT = "/tags"
    SAMPLINGS_ENDPOINT = "/samplings"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the Gamma API client.

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

    async def __aenter__(self) -> "GammaClient":
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

        url = urljoin(self.base_url, endpoint)
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

    async def get_markets(
        self,
        *,
        active: bool | None = None,
        closed: bool | None = None,
        archived: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order: str | None = None,
        ascending: bool | None = None,
        enable_order_book: bool | None = None,
    ) -> list[Market]:
        """
        Get markets from the Gamma API.

        Args:
            active: Filter for active markets
            closed: Filter for closed markets
            archived: Filter for archived markets
            limit: Maximum number of results to return
            offset: Pagination offset
            order: Order by field (e.g., 'volume', 'liquidity')
            ascending: Sort in ascending order (default: descending)
            enable_order_book: Filter for CLOB-enabled markets

        Returns:
            List of Market objects

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                # Get first 10 active markets
                markets = await client.get_markets(active=True, limit=10)
            ```
        """
        params: dict[str, Any] = {}
        if active is not None:
            params["active"] = str(active).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()
        if archived is not None:
            params["archived"] = str(archived).lower()
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if order is not None:
            params["order"] = order
        if ascending is not None:
            params["ascending"] = str(ascending).lower()
        if enable_order_book is not None:
            params["enableOrderBook"] = str(enable_order_book).lower()

        data = await self._request("GET", self.MARKETS_ENDPOINT, params=params)

        try:
            return [Market.model_validate(market) for market in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse markets: {e}")

    async def get_market(self, market_id: str) -> Market:
        """
        Get a specific market by ID.

        Args:
            market_id: The market ID

        Returns:
            Market object

        Raises:
            MarketNotFoundError: If market doesn't exist
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                market = await client.get_market("12")
                print(market.question)
            ```
        """
        try:
            data = await self._request("GET", f"{self.MARKETS_ENDPOINT}/{market_id}")
        except PolymarketAPIError as e:
            if e.status_code == 404:
                raise MarketNotFoundError(market_id)
            raise

        try:
            return Market.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse market: {e}")

    async def get_all_markets(
        self,
        *,
        active: bool | None = None,
        closed: bool | None = None,
        archived: bool | None = None,
        batch_size: int = 100,
    ) -> AsyncIterator[Market]:
        """
        Get all markets with automatic pagination.

        This method yields markets one at a time while automatically handling
        pagination in the background.

        Args:
            active: Filter for active markets
            closed: Filter for closed markets
            archived: Filter for archived markets
            batch_size: Number of markets to fetch per request

        Yields:
            Market objects one at a time

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                async for market in client.get_all_markets(active=True):
                    print(f"{market.question}: ${market.volume_num:.2f}")
            ```
        """
        offset = 0
        while True:
            markets = await self.get_markets(
                active=active,
                closed=closed,
                archived=archived,
                limit=batch_size,
                offset=offset,
            )

            if not markets:
                break

            for market in markets:
                yield market

            if len(markets) < batch_size:
                break

            offset += batch_size

    async def get_events(
        self,
        *,
        active: bool | None = None,
        closed: bool | None = None,
        archived: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order: str | None = None,
        ascending: bool | None = None,
        tag: str | None = None,
    ) -> list[Event]:
        """
        Get events from the Gamma API.

        Args:
            active: Filter for active events
            closed: Filter for closed events
            archived: Filter for archived events
            limit: Maximum number of results to return
            offset: Pagination offset
            order: Order by field (e.g., 'volume', 'liquidity')
            ascending: Sort in ascending order (default: descending)
            tag: Filter by tag slug

        Returns:
            List of Event objects

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                events = await client.get_events(active=True, limit=10)
            ```
        """
        params: dict[str, Any] = {}
        if active is not None:
            params["active"] = str(active).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()
        if archived is not None:
            params["archived"] = str(archived).lower()
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if order is not None:
            params["order"] = order
        if ascending is not None:
            params["ascending"] = str(ascending).lower()
        if tag is not None:
            params["tag"] = tag

        data = await self._request("GET", self.EVENTS_ENDPOINT, params=params)

        try:
            return [Event.model_validate(event) for event in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse events: {e}")

    async def get_event(self, event_id: str) -> Event:
        """
        Get a specific event by ID.

        Args:
            event_id: The event ID

        Returns:
            Event object

        Raises:
            EventNotFoundError: If event doesn't exist
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                event = await client.get_event("2890")
                print(event.title)
            ```
        """
        try:
            data = await self._request("GET", f"{self.EVENTS_ENDPOINT}/{event_id}")
        except PolymarketAPIError as e:
            if e.status_code == 404:
                raise EventNotFoundError(event_id)
            raise

        try:
            return Event.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse event: {e}")

    async def get_all_events(
        self,
        *,
        active: bool | None = None,
        closed: bool | None = None,
        archived: bool | None = None,
        batch_size: int = 100,
    ) -> AsyncIterator[Event]:
        """
        Get all events with automatic pagination.

        This method yields events one at a time while automatically handling
        pagination in the background.

        Args:
            active: Filter for active events
            closed: Filter for closed events
            archived: Filter for archived events
            batch_size: Number of events to fetch per request

        Yields:
            Event objects one at a time

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                async for event in client.get_all_events(active=True):
                    print(f"{event.title}: {event.volume} volume")
            ```
        """
        offset = 0
        while True:
            events = await self.get_events(
                active=active,
                closed=closed,
                archived=archived,
                limit=batch_size,
                offset=offset,
            )

            if not events:
                break

            for event in events:
                yield event

            if len(events) < batch_size:
                break

            offset += batch_size

    async def get_tags(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Tag]:
        """
        Get all available tags from the Gamma API.

        Args:
            limit: Maximum number of results to return
            offset: Pagination offset

        Returns:
            List of Tag objects

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                tags = await client.get_tags(limit=50)
                for tag in tags:
                    print(f"{tag.label} ({tag.slug})")
            ```
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        data = await self._request("GET", self.TAGS_ENDPOINT, params=params)

        try:
            return [Tag.model_validate(tag) for tag in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse tags: {e}")

    async def get_samplings(
        self,
        market: str,
        *,
        fidelity: int | None = None,
        start_ts: int | None = None,
        end_ts: int | None = None,
    ) -> list[Sampling]:
        """
        Get price samplings (historical price data) for a specific market.

        Args:
            market: Market condition ID
            fidelity: Sampling fidelity/resolution (optional)
            start_ts: Start timestamp in seconds (optional)
            end_ts: End timestamp in seconds (optional)

        Returns:
            List of Sampling objects with timestamps and prices

        Raises:
            ValidationError: If response validation fails
            PolymarketAPIError: For API errors

        Example:
            ```python
            async with GammaClient() as client:
                samplings = await client.get_samplings(
                    market="0xe3b423dfad8c22ff75c9899c4e8176f628cf4ad4caa00481764d320e7415f7a9"
                )
                for sample in samplings:
                    print(f"Time: {sample.t}, Price: {sample.p}")
            ```
        """
        params: dict[str, Any] = {"market": market}
        if fidelity is not None:
            params["fidelity"] = fidelity
        if start_ts is not None:
            params["startTs"] = start_ts
        if end_ts is not None:
            params["endTs"] = end_ts

        data = await self._request("GET", self.SAMPLINGS_ENDPOINT, params=params)

        try:
            return [Sampling.model_validate(sample) for sample in data]
        except PydanticValidationError as e:
            raise ValidationError(f"Failed to parse samplings: {e}")
