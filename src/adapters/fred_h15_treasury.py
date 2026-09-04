"""Pure FRED DGS2/DGS10 adapter primitives.

Phase 0 safety: no HTTP requests, no secret persistence, no database writes.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

SOURCE_ID = "macro.fred.h15.dgs2_dgs10"
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
ALLOWED_SERIES = {"DGS2", "DGS10"}


def build_url(*, series_id: str, api_key: str, realtime_start: str, realtime_end: str) -> str:
    if series_id not in ALLOWED_SERIES:
        raise ValueError("unapproved FRED series")
    if not api_key:
        raise ValueError("runtime FRED api_key is required")
    if not realtime_start or not realtime_end:
        raise ValueError("realtime_start and realtime_end are required")
    query = urlencode({
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": realtime_start,
        "realtime_end": realtime_end,
    })
    return f"{BASE_URL}?{query}"


def safe_request_metadata(*, series_id: str, realtime_start: str, realtime_end: str) -> dict[str, str]:
    if series_id not in ALLOWED_SERIES:
        raise ValueError("unapproved FRED series")
    return {
        "source_id": SOURCE_ID,
        "series_id": series_id,
        "realtime_start": realtime_start,
        "realtime_end": realtime_end,
    }


def parse_observations(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
        raise ValueError("invalid FRED observations payload")

    parsed: list[dict[str, object]] = []
    for row in payload["observations"]:
        if not isinstance(row, dict):
            raise ValueError("invalid FRED observation row")
        value = row.get("value")
        if value == ".":
            parsed_value = None
        else:
            try:
                parsed_value = Decimal(str(value))
            except (InvalidOperation, ValueError) as exc:
                raise ValueError("invalid FRED numeric value") from exc
        parsed.append({
            "date": row.get("date"),
            "realtime_start": row.get("realtime_start"),
            "realtime_end": row.get("realtime_end"),
            "value": parsed_value,
        })
    return parsed


def raw_record_metadata(*, observed_at: str, ingested_at: str, content_hash: str) -> dict[str, str]:
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
