"""Pure Binance USD-M Futures funding rate + open interest adapter primitives.

Phase 0 safety: this module performs no HTTP requests and no database writes.
It only builds approved read-only URLs and parses/validates supplied payloads.

Candidate source, not yet approved. See:
docs/architecture/BINANCE_FUTURES_FUNDING_OI_ADAPTER_v0.1.md
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

SOURCE_ID = "derivatives.binance.usdm_futures.btcusdt.funding_oi"
SYMBOL = "BTCUSDT"

FUNDING_RATE_BASE_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
OPEN_INTEREST_HIST_BASE_URL = "https://fapi.binance.com/futures/data/openInterestHist"

MAX_FUNDING_ROWS = 1000
MAX_OPEN_INTEREST_ROWS = 500
ALLOWED_OI_PERIODS = {"5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"}


@dataclass(frozen=True)
class FundingRateRow:
    source_event_at_ms: int
    funding_rate: Decimal
    mark_price: Decimal | None


@dataclass(frozen=True)
class OpenInterestRow:
    source_event_at_ms: int
    sum_open_interest: Decimal
    sum_open_interest_value: Decimal | None


def build_funding_rate_url(
    *,
    start_time_ms: int | None = None,
    end_time_ms: int | None = None,
    limit: int = 1000,
) -> str:
    if limit < 1 or limit > MAX_FUNDING_ROWS:
        raise ValueError("funding rate limit must be between 1 and 1000")
    params: dict[str, object] = {"symbol": SYMBOL, "limit": limit}
    if start_time_ms is not None:
        params["startTime"] = start_time_ms
    if end_time_ms is not None:
        params["endTime"] = end_time_ms
    return f"{FUNDING_RATE_BASE_URL}?{urlencode(params)}"


def build_open_interest_hist_url(
    *,
    period: str = "1h",
    start_time_ms: int | None = None,
    end_time_ms: int | None = None,
    limit: int = 500,
) -> str:
    if period not in ALLOWED_OI_PERIODS:
        raise ValueError("unsupported open interest history period")
    if limit < 1 or limit > MAX_OPEN_INTEREST_ROWS:
        raise ValueError("open interest limit must be between 1 and 500")
    params: dict[str, object] = {"symbol": SYMBOL, "period": period, "limit": limit}
    if start_time_ms is not None:
        params["startTime"] = start_time_ms
    if end_time_ms is not None:
        params["endTime"] = end_time_ms
    return f"{OPEN_INTEREST_HIST_BASE_URL}?{urlencode(params)}"


def parse_funding_rates(payload: object) -> list[FundingRateRow]:
    if not isinstance(payload, list):
        raise ValueError("funding rate payload must be a list")
    if len(payload) > MAX_FUNDING_ROWS:
        raise ValueError("payload exceeds documented 1000-row funding rate limit")

    parsed: list[FundingRateRow] = []
    seen_times: set[int] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("each funding rate row must be an object")
        if row.get("symbol") != SYMBOL:
            raise ValueError("unapproved symbol in funding rate payload")

        funding_time = row.get("fundingTime")
        if not isinstance(funding_time, int):
            raise ValueError("fundingTime must be integer epoch milliseconds")

        try:
            funding_rate = Decimal(str(row.get("fundingRate")))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError("invalid fundingRate value") from exc

        mark_price_raw = row.get("markPrice")
        mark_price: Decimal | None = None
        if mark_price_raw not in (None, ""):
            try:
                mark_price = Decimal(str(mark_price_raw))
            except (InvalidOperation, ValueError) as exc:
                raise ValueError("invalid markPrice value") from exc
            if mark_price < 0:
                raise ValueError("negative markPrice")

        if funding_time in seen_times:
            raise ValueError("duplicate fundingTime in one response")
        seen_times.add(funding_time)

        parsed.append(FundingRateRow(funding_time, funding_rate, mark_price))

    return parsed


def parse_open_interest_hist(payload: object) -> list[OpenInterestRow]:
    if not isinstance(payload, list):
        raise ValueError("open interest payload must be a list")
    if len(payload) > MAX_OPEN_INTEREST_ROWS:
        raise ValueError("payload exceeds documented 500-row open interest limit")

    parsed: list[OpenInterestRow] = []
    seen_times: set[int] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("each open interest row must be an object")
        if row.get("symbol") != SYMBOL:
            raise ValueError("unapproved symbol in open interest payload")

        timestamp = row.get("timestamp")
        if not isinstance(timestamp, int):
            raise ValueError("timestamp must be integer epoch milliseconds")

        try:
            sum_oi = Decimal(str(row.get("sumOpenInterest")))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError("invalid sumOpenInterest value") from exc
        if sum_oi < 0:
            raise ValueError("negative sumOpenInterest")

        sum_oi_value_raw = row.get("sumOpenInterestValue")
        sum_oi_value: Decimal | None = None
        if sum_oi_value_raw not in (None, ""):
            try:
                sum_oi_value = Decimal(str(sum_oi_value_raw))
            except (InvalidOperation, ValueError) as exc:
                raise ValueError("invalid sumOpenInterestValue value") from exc
            if sum_oi_value < 0:
                raise ValueError("negative sumOpenInterestValue")

        if timestamp in seen_times:
            raise ValueError("duplicate timestamp in one response")
        seen_times.add(timestamp)

        parsed.append(OpenInterestRow(timestamp, sum_oi, sum_oi_value))

    return parsed


def raw_record_metadata(
    *,
    dataset: str,
    observed_at: str,
    ingested_at: str,
    content_hash: str,
) -> dict[str, str]:
    """Return Phase 0 provenance fields without backdating availability to event time."""
    if dataset not in ("funding_rate", "open_interest_hist"):
        raise ValueError("dataset must be 'funding_rate' or 'open_interest_hist'")
    if not observed_at or not ingested_at or not content_hash:
        raise ValueError("observed_at, ingested_at and content_hash are required")
    return {
        "source_id": SOURCE_ID,
        "dataset": dataset,
        "observed_at": observed_at,
        "ingested_at": ingested_at,
        "available_at": observed_at,
        "content_hash": content_hash,
        "schema_version": "0.1",
    }
