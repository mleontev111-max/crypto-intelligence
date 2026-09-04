"""Minimal approved-source collector, disabled by default.

Without --write this command performs no HTTP requests and no database writes.
With --write it requires explicit bounded windows, RAW_STORAGE_DIR, FRED_API_KEY,
and a PostgreSQL connection supplied by DATABASE_URL or standard PG* variables.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from typing import Sequence

from src.adapters.coinbase_exchange_candles import build_url as build_coinbase_url
from src.adapters.fred_h15_treasury import build_url as build_fred_url
from src.ingestion.approved_sources import coinbase_payload_to_rows, fred_payload_to_rows
from src.ingestion.postgres_writer import persist_bundle, seed_approved_sources
from src.storage.raw_files import store_raw_bytes
from src.transport.read_only_http import read_only_get


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect approved public sources into RAW + observations")
    parser.add_argument("--write", action="store_true", help="explicitly enable network fetch + configured DB write")
    parser.add_argument("--coinbase-start")
    parser.add_argument("--coinbase-end")
    parser.add_argument("--fred-realtime-date")
    parser.add_argument("--fred-observation-start")
    parser.add_argument("--fred-observation-end")
    return parser


def _require(value: str | None, name: str) -> str:
    if not value:
        raise RuntimeError(f"{name} is required with --write")
    return value


def _fetch_coinbase(*, start: str, end: str, raw_storage_dir: str):
    url = build_coinbase_url(start=start, end=end, granularity=3600)
    result = read_only_get(url)
    digest, payload_ref = store_raw_bytes(
        root=raw_storage_dir,
        body=result.body,
        expected_sha256=result.evidence.sha256_hex,
    )
    observed_at = _dt(result.evidence.received_at)
    raw, rows = coinbase_payload_to_rows(
        payload=json.loads(result.body.decode("utf-8")),
        start=start,
        end=end,
        granularity=3600,
        observed_at=observed_at,
        ingested_at=datetime.now(timezone.utc),
        content_hash=digest,
        payload_ref=payload_ref,
        mime_type=result.evidence.content_type,
    )
    return result, raw, rows


def _fetch_fred(
    *,
    series_id: str,
    api_key: str,
    realtime_date: str,
    observation_start: str,
    observation_end: str,
    raw_storage_dir: str,
):
    url = build_fred_url(
        series_id=series_id,
        api_key=api_key,
        realtime_start=realtime_date,
        realtime_end=realtime_date,
        observation_start=observation_start,
        observation_end=observation_end,
    )
    result = read_only_get(url)
    digest, payload_ref = store_raw_bytes(
        root=raw_storage_dir,
        body=result.body,
        expected_sha256=result.evidence.sha256_hex,
    )
    observed_at = _dt(result.evidence.received_at)
    raw, rows = fred_payload_to_rows(
        payload=json.loads(result.body.decode("utf-8")),
        series_id=series_id,
        realtime_start=realtime_date,
        realtime_end=realtime_date,
        observation_start=observation_start,
        observation_end=observation_end,
        observed_at=observed_at,
        ingested_at=datetime.now(timezone.utc),
        content_hash=digest,
        payload_ref=payload_ref,
        mime_type=result.evidence.content_type,
    )
    return result, raw, rows


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.write:
        print(json.dumps({
            "status": "disabled",
            "network_fetch_performed": False,
            "database_write_performed": False,
            "hint": "pass --write with explicit bounded windows to run the collector",
        }, sort_keys=True))
        return 0

    raw_storage_dir = _require(os.environ.get("RAW_STORAGE_DIR"), "RAW_STORAGE_DIR")
    fred_api_key = _require(os.environ.get("FRED_API_KEY"), "FRED_API_KEY")
    coinbase_start = _require(args.coinbase_start, "--coinbase-start")
    coinbase_end = _require(args.coinbase_end, "--coinbase-end")
    fred_realtime_date = _require(args.fred_realtime_date, "--fred-realtime-date")
    fred_observation_start = _require(args.fred_observation_start, "--fred-observation-start")
    fred_observation_end = _require(args.fred_observation_end, "--fred-observation-end")

    coinbase_result, coinbase_raw, coinbase_rows = _fetch_coinbase(
        start=coinbase_start,
        end=coinbase_end,
        raw_storage_dir=raw_storage_dir,
    )
    fred2_result, fred2_raw, fred2_rows = _fetch_fred(
        series_id="DGS2",
        api_key=fred_api_key,
        realtime_date=fred_realtime_date,
        observation_start=fred_observation_start,
        observation_end=fred_observation_end,
        raw_storage_dir=raw_storage_dir,
    )
    fred10_result, fred10_raw, fred10_rows = _fetch_fred(
        series_id="DGS10",
        api_key=fred_api_key,
        realtime_date=fred_realtime_date,
        observation_start=fred_observation_start,
        observation_end=fred_observation_end,
        raw_storage_dir=raw_storage_dir,
    )

    if not coinbase_rows or not fred2_rows or not fred10_rows:
        raise RuntimeError("each approved source must produce at least one observation")

    import psycopg  # Lazy import: disabled mode has no PostgreSQL dependency.

    conninfo = os.environ.get("DATABASE_URL", "")
    with psycopg.connect(conninfo) as conn:
        seed_approved_sources(conn)
        for raw, rows in (
            (coinbase_raw, coinbase_rows),
            (fred2_raw, fred2_rows),
            (fred10_raw, fred10_rows),
        ):
            persist_bundle(conn, raw, rows)

    summary = {
        "status": "success",
        "persistent_collector_mode": True,
        "scheduled": False,
        "coinbase": {
            "http_status": coinbase_result.evidence.status,
            "safe_url": coinbase_result.evidence.safe_url,
            "sha256": coinbase_raw.content_hash,
            "observations": len(coinbase_rows),
            "payload_ref": coinbase_raw.payload_ref,
        },
        "fred_dgs2": {
            "http_status": fred2_result.evidence.status,
            "safe_url": fred2_result.evidence.safe_url,
            "sha256": fred2_raw.content_hash,
            "observations": len(fred2_rows),
            "payload_ref": fred2_raw.payload_ref,
        },
        "fred_dgs10": {
            "http_status": fred10_result.evidence.status,
            "safe_url": fred10_result.evidence.safe_url,
            "sha256": fred10_raw.content_hash,
            "observations": len(fred10_rows),
            "payload_ref": fred10_raw.payload_ref,
        },
    }
    encoded = json.dumps(summary, sort_keys=True)
    if fred_api_key in encoded:
        raise RuntimeError("FRED secret appeared in collector summary")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
