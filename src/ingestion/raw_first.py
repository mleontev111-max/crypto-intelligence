"""Minimal RAW-first ingestion primitives.

This module deliberately contains no HTTP client and no database client.
It turns already-fetched public source data into deterministic rows suitable
for one PostgreSQL transaction: RAW -> observation -> lineage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid5

_RAW_NAMESPACE = UUID("8e9f02de-73f3-4e1a-b73f-3d78c5e0d1c1")
_OBS_NAMESPACE = UUID("505f57fe-0242-4db5-9e3f-b5c0e726d496")


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def raw_event_id(*, source_id: str, source_record_id: str, content_hash: str) -> UUID:
    if not source_id or not source_record_id or not content_hash:
        raise ValueError("source_id, source_record_id and content_hash are required")
    return uuid5(_RAW_NAMESPACE, f"{source_id}|{source_record_id}|{content_hash}")


def observation_id(*, raw_event_id_value: UUID, metric_id: str, event_at: datetime, ordinal: int = 0) -> UUID:
    if not metric_id:
        raise ValueError("metric_id is required")
    if ordinal < 0:
        raise ValueError("ordinal must be non-negative")
    event_at_utc = _utc(event_at).isoformat()
    return uuid5(_OBS_NAMESPACE, f"{raw_event_id_value}|{metric_id}|{event_at_utc}|{ordinal}")


@dataclass(frozen=True)
class RawEventRow:
    raw_event_id: UUID
    source_id: str
    source_record_id: str
    source_event_at: datetime | None
    provider_published_at: datetime | None
    observed_at: datetime
    ingested_at: datetime
    available_at: datetime
    content_hash: str
    payload_ref: str
    mime_type: str | None = None
    revision_text: str | None = None
    supersedes_raw_event_id: UUID | None = None


@dataclass(frozen=True)
class ObservationRow:
    observation_id: UUID
    raw_event_id: UUID
    metric_id: str
    asset: str
    venue: str | None
    value: Decimal
    unit: str
    event_at: datetime
    available_at: datetime
    quality_status: str
    normalizer_version: str
    revision_text: str | None = None


def build_raw_event(
    *,
    source_id: str,
    source_record_id: str,
    source_event_at: datetime | None,
    provider_published_at: datetime | None,
    observed_at: datetime,
    ingested_at: datetime,
    available_at: datetime,
    content_hash: str,
    payload_ref: str,
    mime_type: str | None = None,
    revision_text: str | None = None,
    supersedes_raw_event_id: UUID | None = None,
) -> RawEventRow:
    observed_at = _utc(observed_at)
    ingested_at = _utc(ingested_at)
    available_at = _utc(available_at)
    source_event_at = _utc(source_event_at) if source_event_at else None
    provider_published_at = _utc(provider_published_at) if provider_published_at else None

    if available_at > ingested_at:
        raise ValueError("available_at cannot be after ingested_at")
    if not payload_ref:
        raise ValueError("payload_ref is required")

    return RawEventRow(
        raw_event_id=raw_event_id(
            source_id=source_id,
            source_record_id=source_record_id,
            content_hash=content_hash,
        ),
        source_id=source_id,
        source_record_id=source_record_id,
        source_event_at=source_event_at,
        provider_published_at=provider_published_at,
        observed_at=observed_at,
        ingested_at=ingested_at,
        available_at=available_at,
        content_hash=content_hash,
        payload_ref=payload_ref,
        mime_type=mime_type,
        revision_text=revision_text,
        supersedes_raw_event_id=supersedes_raw_event_id,
    )


def build_observation(
    *,
    raw: RawEventRow,
    metric_id: str,
    asset: str,
    venue: str | None,
    value: Decimal,
    unit: str,
    event_at: datetime,
    available_at: datetime,
    quality_status: str,
    normalizer_version: str,
    ordinal: int = 0,
    revision_text: str | None = None,
) -> ObservationRow:
    event_at = _utc(event_at)
    available_at = _utc(available_at)
    if available_at < raw.available_at:
        raise ValueError("observation available_at cannot predate RAW available_at")
    if quality_status not in {"valid", "suspect", "missing_repaired"}:
        raise ValueError("unsupported quality_status")

    return ObservationRow(
        observation_id=observation_id(
            raw_event_id_value=raw.raw_event_id,
            metric_id=metric_id,
            event_at=event_at,
            ordinal=ordinal,
        ),
        raw_event_id=raw.raw_event_id,
        metric_id=metric_id,
        asset=asset,
        venue=venue,
        value=Decimal(value),
        unit=unit,
        event_at=event_at,
        available_at=available_at,
        quality_status=quality_status,
        normalizer_version=normalizer_version,
        revision_text=revision_text,
    )
