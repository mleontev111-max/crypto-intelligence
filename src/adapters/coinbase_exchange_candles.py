"""Pure Coinbase Exchange BTC-USD candle adapter primitives.

Phase 0 safety: this module performs no HTTP requests and no database writes.
It only builds an approved read-only URL and parses/validates supplied payloads.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

SOURCE_ID = "market.coinbase.exchange.btcusd.candles"
BASE_URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
ALLOWED_GRANULARITIES = {60, 300, 900, 3600, 21600, 86400}
MAX_CANDLES = 300


@dataclass(frozen=True)
class Candle:
    source_event_at_seconds: int
    low: Decimal
    high: Decimal
    open: Decimal
    close: Decimal
    volume: Decimal


def build_url(*, start: str, end: str, granularity: int = 3600) -> str:
    if granularity not in ALLOWED_GRANULARITIES:
        raise ValueError("unsupported Coinbase Exchange candle granularity")
    if not start or not end:
        raise ValueError("start and end are required")
    return f"{BASE_URL}?{urlencode({'start': start, 'end': end, 'granularity': granularity})}"


def parse_candles(payload: object) -> list[Candle]:
    if not isinstance(payload, list):
        raise ValueError("Coinbase candle payload must be a list")
    if len(payload) > MAX_CANDLES:
        raise ValueError("payload exceeds documented 300-candle response limit")

    parsed: list[Candle] = []
    seen_times: set[int] = set()
    for row in payload:
        if not isinstance(row, list) or len(row) != 6:
            raise ValueError("each candle must contain exactly 6 fields")
        timestamp, low, high, open_, close, volume = row
        if not isinstance(timestamp, int):
            raise ValueError("candle timestamp must be integer epoch seconds")
        try:
            d_low = Decimal(str(low))
            d_high = Decimal(str(high))
            d_open = Decimal(str(open_))
            d_close = Decimal(str(close))
            d_volume = Decimal(str(volume))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("invalid numeric candle field") from exc

        if min(d_low, d_high, d_open, d_close, d_volume) < 0:
            raise ValueError("negative OHLCV value")
        if d_low > d_high:
            raise ValueError("low exceeds high")
        if not (d_low <= d_open <= d_high and d_low <= d_close <= d_high):
            raise ValueError("open/close outside low-high range")
        if timestamp in seen_times:
            raise ValueError("duplicate candle timestamp in one response")
        seen_times.add(timestamp)
        parsed.append(Candle(timestamp, d_low, d_high, d_open, d_close, d_volume))

    return parsed


def raw_record_metadata(*, observed_at: str, ingested_at: str, content_hash: str) -> dict[str, str]:
    """Return Phase 0 provenance fields without backdating availability to candle time."""
    if not observed_at or not ingested_at or not content_hash:
        raise ValueError("observed_at, ingested_at and content_hash are required")
    return {
        "source_id": SOURCE_ID,
        "observed_at": observed_at,
        "ingested_at": ingested_at,
        "available_at": observed_at,
        "content_hash": content_hash,
        "schema_version": "0.1",
    }
