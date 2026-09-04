"""Map approved adapter payloads into minimal RAW-first ingestion rows.

No HTTP client and no database client live here. The caller supplies an already
fetched payload plus response evidence. The result can then be written in one
ordinary PostgreSQL transaction.
"""

from __future__ import annotations

from datetime import datetime, time, timezone
from decimal import Decimal

from src.adapters.coinbase_exchange_candles import SOURCE_ID as COINBASE_SOURCE_ID, parse_candles
from src.adapters.fred_h15_treasury import SOURCE_ID as FRED_SOURCE_ID, parse_observations
from src.ingestion.raw_first import ObservationRow, RawEventRow, build_observation, build_raw_event


def _iso_date_utc(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("date must be an ISO date string")
    try:
        return datetime.combine(datetime.fromisoformat(value).date(), time.min, tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("invalid ISO date") from exc


def coinbase_request_record_id(*, start: str, end: str, granularity: int) -> str:
    if not start or not end or granularity <= 0:
        raise ValueError("start, end and positive granularity are required")
    return f"BTC-USD|start={start}|end={end}|granularity={granularity}"


def fred_request_record_id(*, series_id: str, realtime_start: str, realtime_end: str) -> str:
    if not series_id or not realtime_start or not realtime_end:
        raise ValueError("series_id and realtime bounds are required")
    return f"{series_id}|realtime_start={realtime_start}|realtime_end={realtime_end}"


def coinbase_payload_to_rows(
    *,
    payload: object,
    start: str,
    end: str,
    granularity: int,
    observed_at: datetime,
    ingested_at: datetime,
    content_hash: str,
    payload_ref: str,
    mime_type: str | None = "application/json",
) -> tuple[RawEventRow, list[ObservationRow]]:
    candles = parse_candles(payload)
    raw = build_raw_event(
        source_id=COINBASE_SOURCE_ID,
        source_record_id=coinbase_request_record_id(start=start, end=end, granularity=granularity),
        source_event_at=None,
        provider_published_at=None,
        observed_at=observed_at,
        ingested_at=ingested_at,
        available_at=observed_at,
        content_hash=content_hash,
        payload_ref=payload_ref,
        mime_type=mime_type,
    )

    rows: list[ObservationRow] = []
    metrics = (
        ("market.open", "open", "USD"),
        ("market.high", "high", "USD"),
        ("market.low", "low", "USD"),
        ("market.close", "close", "USD"),
        ("market.volume", "volume", "BTC"),
    )
    for candle in candles:
        event_at = datetime.fromtimestamp(candle.source_event_at_seconds, tz=timezone.utc)
        for ordinal, (metric_id, field_name, unit) in enumerate(metrics):
            rows.append(
                build_observation(
                    raw=raw,
                    metric_id=metric_id,
                    asset="BTC",
                    venue="coinbase",
                    value=Decimal(getattr(candle, field_name)),
                    unit=unit,
                    event_at=event_at,
                    available_at=raw.available_at,
                    quality_status="valid",
                    normalizer_version="coinbase-candles-v0.1",
                    ordinal=ordinal,
                )
            )
    return raw, rows


def fred_payload_to_rows(
    *,
    payload: object,
    series_id: str,
    realtime_start: str,
    realtime_end: str,
    observed_at: datetime,
    ingested_at: datetime,
    content_hash: str,
    payload_ref: str,
    mime_type: str | None = "application/json",
) -> tuple[RawEventRow, list[ObservationRow]]:
    observations = parse_observations(payload)
    raw = build_raw_event(
        source_id=FRED_SOURCE_ID,
        source_record_id=fred_request_record_id(
            series_id=series_id,
            realtime_start=realtime_start,
            realtime_end=realtime_end,
        ),
        source_event_at=None,
        provider_published_at=None,
        observed_at=observed_at,
        ingested_at=ingested_at,
        available_at=observed_at,
        content_hash=content_hash,
        payload_ref=payload_ref,
        mime_type=mime_type,
    )

    rows: list[ObservationRow] = []
    for ordinal, item in enumerate(observations):
        value = item["value"]
        if value is None:
            continue
        event_at = _iso_date_utc(item["date"])
        rows.append(
            build_observation(
                raw=raw,
                metric_id=f"macro.fred.{series_id.lower()}",
                asset="US_RATES",
                venue="fred",
                value=Decimal(value),
                unit="percent",
                event_at=event_at,
                available_at=raw.available_at,
                quality_status="valid",
                normalizer_version="fred-h15-v0.1",
                ordinal=ordinal,
            )
        )
    return raw, rows
