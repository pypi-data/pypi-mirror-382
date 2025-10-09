# aiopolymarket

A comprehensive, type-safe async Python client for [Polymarket's APIs](https://docs.polymarket.com/).

Supports both:
- **Gamma Markets API** - Market data, events, tags, and price history
- **Data API** - User positions, trades, activity, and holder information

## Features

- **Fully async/await native** - Built with `aiohttp` for high-performance async operations
- **Type-safe** - Comprehensive type hints and Pydantic models for all API responses
- **Comprehensive coverage** - All endpoints and query parameters supported
- **Automatic pagination** - Convenient async iterators for fetching all markets/events
- **Robust error handling** - Custom exceptions with automatic retry logic and exponential backoff
- **Production-ready** - Connection pooling, timeout handling, and proper resource cleanup
- **Dual APIs** - Both GammaClient (market data) and DataClient (trading data)

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### GammaClient - Market Data

```python
import asyncio
from aiopolymarket import GammaClient

async def main():
    # Use as a context manager for automatic cleanup
    async with GammaClient() as client:
        # Get top markets by volume
        markets = await client.get_markets(
            active=True,
            order="volume",
            limit=10
        )

        for market in markets:
            print(f"{market.question}")
            print(f"  Volume: ${market.volume_num:,.2f}")
            print(f"  Outcomes: {market.outcomes}")
            print()

asyncio.run(main())
```

### DataClient - Trading Data

```python
import asyncio
from aiopolymarket import DataClient

async def main():
    async with DataClient() as client:
        # Get user positions
        positions = await client.get_positions(
            user="0x123...",
            size_threshold=100
        )

        for position in positions:
            print(f"Market: {position.market}")
            print(f"Size: {position.size}")

asyncio.run(main())
```

## Usage Examples

### GammaClient Examples

#### Getting Markets

```python
async with GammaClient() as client:
    # Get markets with sorting and filtering
    markets = await client.get_markets(
        active=True,
        order="volume",
        ascending=False,
        enable_order_book=True,
        limit=100
    )

    # Get a specific market by ID
    market = await client.get_market("12")
    print(f"{market.question}: {market.description}")

    # Iterate through all active markets
    async for market in client.get_all_markets(active=True):
        print(f"{market.question}: ${market.volume_num:,.2f}")
```

#### Getting Events

```python
async with GammaClient() as client:
    # Get events with filtering and sorting
    events = await client.get_events(
        active=True,
        tag="politics",
        order="volume",
        limit=10
    )

    # Get a specific event by ID
    event = await client.get_event("2890")
    print(f"{event.title}")
    print(f"Markets: {len(event.markets)}")

    # Iterate through all events
    async for event in client.get_all_events(active=True):
        print(f"{event.title}: {event.volume} volume")
```

#### Getting Tags

```python
async with GammaClient() as client:
    # Get all available tags
    tags = await client.get_tags(limit=100)

    for tag in tags:
        print(f"{tag.label} ({tag.slug})")
```

#### Getting Price History

```python
async with GammaClient() as client:
    # Get price samplings for a market
    samplings = await client.get_samplings(
        market="0xe3b423dfad8c22ff75c9899c4e8176f628cf4ad4caa00481764d320e7415f7a9",
        fidelity=100
    )

    for sample in samplings:
        print(f"Time: {sample.t}, Price: {sample.p}")
```

### DataClient Examples

#### Getting Positions

```python
async with DataClient() as client:
    # Get user positions
    positions = await client.get_positions(
        user="0x123...",
        size_threshold=100,
        limit=50,
        sort_by="CURRENT"
    )

    for position in positions:
        print(f"Market: {position.market}")
        print(f"Size: {position.size}, Value: ${position.value}")
```

#### Getting Trades

```python
async with DataClient() as client:
    # Get user trades
    trades = await client.get_trades(
        user="0x123...",
        side="BUY",
        filter_type="CASH",
        limit=100
    )

    for trade in trades:
        print(f"{trade.side} {trade.size} @ ${trade.price}")
```

#### Getting Activity

```python
async with DataClient() as client:
    # Get on-chain activity
    activity = await client.get_activity(
        user="0x123...",
        activity_type="TRADE",
        limit=50
    )

    for act in activity:
        print(f"Type: {act.type}, Time: {act.timestamp}")
```

#### Getting Holders

```python
async with DataClient() as client:
    # Get top holders of a market
    holders = await client.get_holders(
        market="0xe3b423dfad8c22ff75c9899c4e8176f628cf4ad4caa00481764d320e7415f7a9",
        limit=20
    )

    for holder in holders:
        print(f"User: {holder.user}, Size: {holder.size}")
```

#### Getting Portfolio Value

```python
async with DataClient() as client:
    # Get total portfolio value
    value = await client.get_value(user="0x123...")
    print(f"Total portfolio value: ${value:,.2f}")
```

### Working with Market Data

```python
async with GammaClient() as client:
    markets = await client.get_markets(active=True, limit=10)

    for market in markets:
        # Access all market fields with full type safety
        print(f"Question: {market.question}")
        print(f"Category: {market.category}")
        print(f"Outcomes: {market.outcomes}")
        print(f"Prices: {market.outcome_prices}")
        print(f"Volume (24h): ${market.volume_24hr:,.2f}")
        print(f"Liquidity: ${market.liquidity_num:,.2f}")
        print(f"Best Bid: {market.best_bid}")
        print(f"Best Ask: {market.best_ask}")
        print(f"CLOB Token IDs: {market.clob_token_ids}")

        # Access nested events
        for event in market.events:
            print(f"  Event: {event.title}")
```

### Error Handling

```python
from aiopolymarket import (
    GammaClient,
    MarketNotFoundError,
    RateLimitError,
    NetworkError,
    PolymarketAPIError
)

async with GammaClient() as client:
    try:
        market = await client.get_market("nonexistent")
    except MarketNotFoundError as e:
        print(f"Market not found: {e.market_id}")
    except RateLimitError:
        print("Rate limit exceeded, please try again later")
    except NetworkError as e:
        print(f"Network error: {e.message}")
    except PolymarketAPIError as e:
        print(f"API error: {e.message} (status: {e.status_code})")
```

### Custom Configuration

```python
# Configure timeout, retries, and base URL
client = GammaClient(
    timeout=60.0,           # 60 second timeout
    max_retries=5,          # 5 retry attempts
    retry_delay=2.0,        # 2 second initial delay (exponential backoff)
    base_url="https://gamma-api.polymarket.com"  # Custom base URL
)

async with client:
    markets = await client.get_markets(active=True)
```

## API Reference

### `GammaClient`

Main client class for interacting with the Gamma Markets API.

#### Methods

**Markets:**
- `async get_markets(*, active, closed, archived, limit, offset, order, ascending, enable_order_book) -> list[Market]`
  - Get markets with optional filtering, sorting, and pagination
- `async get_market(market_id: str) -> Market`
  - Get a specific market by ID
- `async get_all_markets(*, active, closed, archived, batch_size) -> AsyncIterator[Market]`
  - Async iterator that yields all markets with automatic pagination

**Events:**
- `async get_events(*, active, closed, archived, limit, offset, order, ascending, tag) -> list[Event]`
  - Get events with optional filtering, sorting, and pagination
- `async get_event(event_id: str) -> Event`
  - Get a specific event by ID
- `async get_all_events(*, active, closed, archived, batch_size) -> AsyncIterator[Event]`
  - Async iterator that yields all events with automatic pagination

**Tags:**
- `async get_tags(*, limit, offset) -> list[Tag]`
  - Get all available tags

**Price History:**
- `async get_samplings(market: str, *, fidelity, start_ts, end_ts) -> list[Sampling]`
  - Get price samplings (historical price data) for a market

### `DataClient`

Client class for interacting with the Polymarket Data API.

#### Methods

**Positions:**
- `async get_positions(user: str, *, market, size_threshold, limit, sort_by) -> list[Position]`
  - Get positions for a user

**Trades:**
- `async get_trades(*, user, market, taker_only, filter_type, side, limit) -> list[Trade]`
  - Get trades for a user or market

**Activity:**
- `async get_activity(user: str, *, market, activity_type, start, end, limit) -> list[Activity]`
  - Get on-chain activity for a user

**Holders:**
- `async get_holders(market: str, *, limit) -> list[Holder]`
  - Get top holders of a market

**Value:**
- `async get_value(user: str, *, market) -> float`
  - Get total USD value of a user's positions

### Models

All models are Pydantic v2 models with full type safety:

**Gamma API Models:**
- `Market` - Complete market data (86+ fields)
- `Event` - Event data with nested markets (40+ fields)
- `Series` - Market series information
- `Tag` - Market categorization tags
- `Sampling` - Price sampling data with timestamps

**Data API Models:**
- `Position` - User position data
- `Trade` - Trade information
- `Activity` - On-chain activity records
- `Holder` - Market holder information

### Exceptions

- `PolymarketAPIError` - Base exception for all API errors
- `MarketNotFoundError` - Market not found (404)
- `EventNotFoundError` - Event not found (404)
- `RateLimitError` - Rate limit exceeded (429)
- `ValidationError` - Response validation failed
- `NetworkError` - Network-related errors

## Type Safety

All responses are validated using Pydantic models:

```python
async with GammaClient() as client:
    market = await client.get_market("12")

    # Full IDE autocomplete and type checking
    question: str = market.question
    volume: float = market.volume_num
    outcomes: list[str] = market.outcomes
    prices: list[str] = market.outcome_prices
```

## Development

This client is built with:
- `aiohttp` - Async HTTP client
- `pydantic` v2 - Data validation and type safety


## Resources

- [Polymarket Documentation](https://docs.polymarket.com/)
- [Gamma API Documentation](https://docs.polymarket.com/developers/gamma-markets-api/overview)
- [Polymarket Website](https://polymarket.com/)
