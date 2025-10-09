"""
Pydantic models for the Polymarket Gamma API.

These models provide type-safe representations of API responses.
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .enums import MarketType, SortBy


class Tag(BaseModel):
    """Market tag model."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    label: str
    slug: str
    force_show: bool | None = Field(None, alias="forceShow")
    published_at: datetime | None = Field(None, alias="publishedAt")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    @field_validator("published_at", "created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
        """Parse datetime from various formats."""
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Try ISO format
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S.%f%z",
            ]:
                try:
                    return datetime.strptime(
                        v.replace("+00", ""), fmt.replace("%z", "")
                    )
                except ValueError:
                    continue
        return None


class Sampling(BaseModel):
    """Market price sampling model."""

    model_config = ConfigDict(populate_by_name=True)

    t: int  # Unix timestamp
    p: float  # Price


class Position(BaseModel):
    """User position model from Data API."""

    model_config = ConfigDict(populate_by_name=True)

    user: str
    market: str
    asset_id: str = Field(alias="assetId")
    size: float
    value: float | None = None


class Trade(BaseModel):
    """Trade model from Data API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    timestamp: int
    market: str
    asset_id: str = Field(alias="assetId")
    side: str  # "BUY" or "SELL"
    size: float
    price: float
    fee: float | None = None
    type: str | None = None  # "MAKER" or "TAKER"


class Activity(BaseModel):
    """On-chain activity model from Data API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    timestamp: int
    user: str
    market: str | None = None
    type: str  # "TRADE", "SPLIT", "MERGE", etc.
    transaction_hash: str | None = Field(None, alias="transactionHash")


class Holder(BaseModel):
    """Market holder model from Data API."""

    model_config = ConfigDict(populate_by_name=True)

    user: str
    market: str
    asset_id: str = Field(alias="assetId")
    size: float
    value: float | None = None


class Series(BaseModel):
    """Market series model."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    ticker: str | None = None
    slug: str | None = None
    title: str | None = None
    series_type: str | None = Field(None, alias="seriesType")
    recurrence: str | None = None
    image: str | None = None
    icon: str | None = None
    layout: str | None = None
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    new: bool | None = None
    featured: bool | None = None
    restricted: bool | None = None
    published_at: datetime | None = Field(None, alias="publishedAt")
    created_by: int | None = Field(None, alias="createdBy")
    updated_by: int | None = Field(None, alias="updatedBy")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    comments_enabled: bool | None = Field(None, alias="commentsEnabled")
    competitive: float | None = None
    volume_24hr: float | None = Field(None, alias="volume24hr")
    start_date: datetime | None = Field(None, alias="startDate")
    comment_count: int | None = Field(None, alias="commentCount")

    @field_validator(
        "published_at", "created_at", "updated_at", "start_date", mode="before"
    )
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
        """Parse datetime from various formats."""
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S%z",
            ]:
                try:
                    return datetime.strptime(
                        v.replace("+00", ""), fmt.replace("%z", "")
                    )
                except ValueError:
                    continue
        return None


class Market(BaseModel):
    """Polymarket market model with complete field definitions."""

    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, coerce_numbers_to_str=True
    )

    # Core identification fields
    id: str
    question: str
    condition_id: str = Field(alias="conditionId")
    slug: str

    # Visual assets
    twitter_card_image: str | None = Field(None, alias="twitterCardImage")
    image: str | None = None
    icon: str | None = None

    # Temporal fields
    end_date: datetime | None = Field(None, alias="endDate")
    end_date_iso: str | None = Field(None, alias="endDateIso")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    closed_time: datetime | None = Field(None, alias="closedTime")

    # Market metadata
    category: str | None = None
    description: str | None = None
    market_type: MarketType | None = Field(None, alias="marketType")

    # Outcomes and pricing (stored as JSON strings in API)
    outcomes: list[str] = Field(default_factory=list)
    outcome_prices: list[str] = Field(default_factory=list, alias="outcomePrices")
    clob_token_ids: list[str] = Field(default_factory=list, alias="clobTokenIds")

    # Financial metrics
    liquidity: str | None = None
    liquidity_num: float | None = Field(None, alias="liquidityNum")
    volume: str | None = None
    volume_num: float | None = Field(None, alias="volumeNum")
    volume_24hr: float | None = Field(None, alias="volume24hr")
    volume_1wk: float | None = Field(None, alias="volume1wk")
    volume_1mo: float | None = Field(None, alias="volume1mo")
    volume_1yr: float | None = Field(None, alias="volume1yr")

    # AMM vs CLOB volume breakdown
    volume_1wk_amm: float | None = Field(None, alias="volume1wkAmm")
    volume_1mo_amm: float | None = Field(None, alias="volume1moAmm")
    volume_1yr_amm: float | None = Field(None, alias="volume1yrAmm")
    volume_1wk_clob: float | None = Field(None, alias="volume1wkClob")
    volume_1mo_clob: float | None = Field(None, alias="volume1moClob")
    volume_1yr_clob: float | None = Field(None, alias="volume1yrClob")

    # Status flags
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    restricted: bool | None = None
    ready: bool | None = None
    funded: bool | None = None
    approved: bool | None = None

    # Blockchain fields
    market_maker_address: str | None = Field(None, alias="marketMakerAddress")

    # Management fields
    updated_by: str | int | None = Field(None, alias="updatedBy")
    mailchimp_tag: str | None = Field(None, alias="mailchimpTag")
    has_reviewed_dates: bool | None = Field(None, alias="hasReviewedDates")
    ready_for_cron: bool | None = Field(None, alias="readyForCron")

    # FPMM fields
    fpmm_live: bool | None = Field(None, alias="fpmmLive")

    # Nested relationships
    events: list["Event"] = Field(default_factory=list)

    # Creator
    creator: str | None = None

    # CYOM (Create Your Own Market)
    cyom: bool | None = None

    # Competitive scoring
    competitive: float | None = None

    # Notifications
    pager_duty_notification_enabled: bool | None = Field(
        None, alias="pagerDutyNotificationEnabled"
    )

    # Rewards
    rewards_min_size: float | None = Field(None, alias="rewardsMinSize")
    rewards_max_spread: float | None = Field(None, alias="rewardsMaxSpread")

    # Market metrics
    spread: float | None = None
    one_day_price_change: float | None = Field(None, alias="oneDayPriceChange")
    one_hour_price_change: float | None = Field(None, alias="oneHourPriceChange")
    one_week_price_change: float | None = Field(None, alias="oneWeekPriceChange")
    one_month_price_change: float | None = Field(None, alias="oneMonthPriceChange")
    one_year_price_change: float | None = Field(None, alias="oneYearPriceChange")
    last_trade_price: float | None = Field(None, alias="lastTradePrice")
    best_bid: float | None = Field(None, alias="bestBid")
    best_ask: float | None = Field(None, alias="bestAsk")

    # Configuration flags
    clear_book_on_start: bool | None = Field(None, alias="clearBookOnStart")
    manual_activation: bool | None = Field(None, alias="manualActivation")
    neg_risk_other: bool | None = Field(None, alias="negRiskOther")

    # UMA resolution
    uma_resolution_statuses: list[Any] = Field(
        default_factory=list, alias="umaResolutionStatuses"
    )

    # Deployment status
    pending_deployment: bool | None = Field(None, alias="pendingDeployment")
    deploying: bool | None = None

    # Feature flags
    rfq_enabled: bool | None = Field(None, alias="rfqEnabled")
    holding_rewards_enabled: bool | None = Field(None, alias="holdingRewardsEnabled")
    fees_enabled: bool | None = Field(None, alias="feesEnabled")

    # Additional fields from nested market responses
    resolution_source: str | None = Field(None, alias="resolutionSource")
    start_date: datetime | None = Field(None, alias="startDate")
    start_date_iso: str | None = Field(None, alias="startDateIso")
    fee: float | None = None
    wide_format: bool | None = Field(None, alias="wideFormat")
    sent_discord: bool | None = Field(None, alias="sentDiscord")
    submitted_by: int | str | None = Field(None, alias="submittedBy")
    twitter_card_location: str | None = Field(None, alias="twitterCardLocation")
    twitter_card_last_refreshed: datetime | None = Field(
        None, alias="twitterCardLastRefreshed"
    )
    resolved_by: int | str | None = Field(None, alias="resolvedBy")

    @field_validator(
        "outcomes",
        "outcome_prices",
        "clob_token_ids",
        "uma_resolution_statuses",
        mode="before",
    )
    @classmethod
    def parse_json_list(cls, v: Any) -> list[Any]:
        """Parse JSON-encoded list fields."""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return []

    @field_validator(
        "end_date",
        "created_at",
        "updated_at",
        "closed_time",
        "start_date",
        "twitter_card_last_refreshed",
        mode="before",
    )
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
        """Parse datetime from various formats."""
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Try multiple datetime formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S.%f%z",
            ]:
                try:
                    return datetime.strptime(
                        v.replace("+00", ""), fmt.replace("%z", "")
                    )
                except ValueError:
                    continue
        return None


class Event(BaseModel):
    """Polymarket event model."""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    # Core fields
    id: str
    ticker: str | None = None
    slug: str
    title: str
    description: str | None = None

    # Resolution
    resolution_source: str | None = Field(None, alias="resolutionSource")

    # Temporal fields
    start_date: datetime | None = Field(None, alias="startDate")
    creation_date: datetime | None = Field(None, alias="creationDate")
    end_date: datetime | None = Field(None, alias="endDate")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    closed_time: datetime | None = Field(None, alias="closedTime")
    published_at: datetime | None = Field(None, alias="published_at")

    # Visual assets
    image: str | None = None
    icon: str | None = None

    # Status flags
    active: bool | None = None
    closed: bool | None = None
    archived: bool | None = None
    new: bool | None = None
    featured: bool | None = None
    restricted: bool | None = None

    # Financial metrics
    liquidity: float | None = None
    liquidity_amm: float | None = Field(None, alias="liquidityAmm")
    liquidity_clob: float | None = Field(None, alias="liquidityClob")
    volume: float | None = None
    volume_24hr: float | None = Field(None, alias="volume24hr")
    volume_1wk: float | None = Field(None, alias="volume1wk")
    volume_1mo: float | None = Field(None, alias="volume1mo")
    volume_1yr: float | None = Field(None, alias="volume1yr")
    open_interest: float | None = Field(None, alias="openInterest")

    # Sorting
    sort_by: SortBy | None = Field(None, alias="sortBy")

    # Category
    category: str | None = None

    # Competition
    competitive: float | None = None

    # Comments
    comment_count: int | None = Field(None, alias="commentCount")

    # Nested relationships
    markets: list[Market] = Field(default_factory=list)
    series: list[Series] = Field(default_factory=list)
    tags: list[Tag] = Field(default_factory=list)

    # CYOM
    cyom: bool | None = None

    # Display options
    show_all_outcomes: bool | None = Field(None, alias="showAllOutcomes")
    show_market_images: bool | None = Field(None, alias="showMarketImages")

    # Risk management
    enable_neg_risk: bool | None = Field(None, alias="enableNegRisk")
    neg_risk_augmented: bool | None = Field(None, alias="negRiskAugmented")

    # Series relationship
    series_slug: str | None = Field(None, alias="seriesSlug")

    # Deployment status
    pending_deployment: bool | None = Field(None, alias="pendingDeployment")
    deploying: bool | None = None

    @field_validator(
        "start_date",
        "creation_date",
        "end_date",
        "created_at",
        "updated_at",
        "closed_time",
        "published_at",
        mode="before",
    )
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
        """Parse datetime from various formats."""
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S%z",
            ]:
                try:
                    return datetime.strptime(
                        v.replace("+00", ""), fmt.replace("%z", "")
                    )
                except ValueError:
                    continue
        return None


# Resolve forward references for circular dependencies
Market.model_rebuild()
Event.model_rebuild()
