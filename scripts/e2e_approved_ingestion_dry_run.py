"""Ephemeral CI-only end-to-end ingestion dry run for approved public sources.

This script is intentionally narrow: it fetches one small fixed Coinbase window and
bounded FRED DGS2/DGS10 windows, maps them to RAW/observation rows, and writes them
to the PostgreSQL instance provided by the caller. It is designed for disposable
GitHub Actions PostgreSQL only while live_ingestion_allowed remains false.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os

import psycopg

from src.adapters.coinbase_exchange_candles import build_url as build_coinbase_url
from src.adapters.fred_h15_treasury import build_url as build_fred_url
from src.ingestion.approved_sources import coinbase_payload_to_rows, fred_payload_to_rows
from src.transport.read_only_http import read_only_get

COINBASE_START = "2026-09-01T00:00:00Z"
COINBASE_END = "2026-09-01T03:00:00Z"
COINBASE_GRANULARITY = 3600
FRED_REALTIME = "2026-09-01"
FRED_OBSERVATION_START = "2026-08-25"
FRED_OBSERVATION_END = "2026-09-01"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _seed_sources(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO data_sources(
              source_id,category,provider,dataset,status,point_in_time_rating,
              revision_policy,terms_review_status
            ) VALUES
              ('market.coinbase.exchange.btcusd.candles','market','Coinbase Exchange','BTC-USD candles','approved','conditional','append','reviewed'),
              ('macro.fred.h15.dgs2_dgs10','macro','FRED','H.15 DGS2/DGS10','approved','conditional','append','reviewed')
            ON CONFLICT (source_id) DO NOTHING
            """
        )
    conn.commit()


def _persist(conn: psycopg.Connection, raw, observations) -> None:
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw_events(
                  raw_event_id,source_id,source_record_id,source_event_at,
                  provider_published_at,observed_at,ingested_at,available_at,
                  revision_text,supersedes_raw_event_id,content_hash,payload_ref,mime_type
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (raw_event_id) DO NOTHING
                """,
                (
                    raw.raw_event_id, raw.source_id, raw.source_record_id, raw.source_event_at,
                    raw.provider_published_at, raw.observed_at, raw.ingested_at, raw.available_at,
                    raw.revision_text, raw.supersedes_raw_event_id, raw.content_hash, raw.payload_ref,
                    raw.mime_type,
                ),
            )
            for row in observations:
                cur.execute(
                    """
                    INSERT INTO observations(
                      observation_id,metric_id,asset,venue,value,unit,event_at,available_at,
                      revision_text,quality_status,normalizer_version
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (observation_id) DO NOTHING
                    """,
                    (
                        row.observation_id, row.metric_id, row.asset, row.venue, row.value,
                        row.unit, row.event_at, row.available_at, row.revision_text,
                        row.quality_status, row.normalizer_version,
                    ),
                )
                cur.execute(
                    """
                    INSERT INTO observation_raw_events(observation_id,raw_event_id)
                    VALUES (%s,%s)
                    ON CONFLICT DO NOTHING
                    """,
                    (row.observation_id, row.raw_event_id),
                )


def _fetch_coinbase():
    url = build_coinbase_url(
        start=COINBASE_START,
        end=COINBASE_END,
        granularity=COINBASE_GRANULARITY,
    )
    result = read_only_get(url)
    observed_at = _dt(result.evidence.received_at)
    ingested_at = datetime.now(timezone.utc)
    payload = json.loads(result.body.decode("utf-8"))
    raw, rows = coinbase_payload_to_rows(
        payload=payload,
        start=COINBASE_START,
        end=COINBASE_END,
        granularity=COINBASE_GRANULARITY,
        observed_at=observed_at,
        ingested_at=ingested_at,
        content_hash=result.evidence.sha256_hex,
        payload_ref=f"sha256:{result.evidence.sha256_hex}",
        mime_type=result.evidence.content_type,
    )
    return result, raw, rows


def _fetch_fred(series_id: str, api_key: str):
    url = build_fred_url(
        series_id=series_id,
        api_key=api_key,
        realtime_start=FRED_REALTIME,
        realtime_end=FRED_REALTIME,
        observation_start=FRED_OBSERVATION_START,
        observation_end=FRED_OBSERVATION_END,
    )
    result = read_only_get(url)
    observed_at = _dt(result.evidence.received_at)
    ingested_at = datetime.now(timezone.utc)
    payload = json.loads(result.body.decode("utf-8"))
    raw, rows = fred_payload_to_rows(
        payload=payload,
        series_id=series_id,
        realtime_start=FRED_REALTIME,
        realtime_end=FRED_REALTIME,
        observation_start=FRED_OBSERVATION_START,
        observation_end=FRED_OBSERVATION_END,
        observed_at=observed_at,
        ingested_at=ingested_at,
        content_hash=result.evidence.sha256_hex,
        payload_ref=f"sha256:{result.evidence.sha256_hex}",
        mime_type=result.evidence.content_type,
    )
    return result, raw, rows


def _verify(conn: psycopg.Connection, expected_raw_ids, expected_observation_ids) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM raw_events WHERE raw_event_id = ANY(%s)", (list(expected_raw_ids),))
        raw_count = cur.fetchone()[0]
        cur.execute(
            "SELECT count(*) FROM observations WHERE observation_id = ANY(%s)",
            (list(expected_observation_ids),),
        )
        observation_count = cur.fetchone()[0]
        cur.execute(
            "SELECT count(*) FROM observation_raw_events WHERE observation_id = ANY(%s)",
            (list(expected_observation_ids),),
        )
        lineage_count = cur.fetchone()[0]
        cur.execute(
            """
            SELECT count(*)
            FROM observations o
            JOIN observation_raw_events l USING (observation_id)
            JOIN raw_events r USING (raw_event_id)
            WHERE o.observation_id = ANY(%s) AND o.available_at < r.available_at
            """,
            (list(expected_observation_ids),),
        )
        pit_violations = cur.fetchone()[0]
    if raw_count != len(expected_raw_ids):
        raise RuntimeError("unexpected RAW row count")
    if observation_count != len(expected_observation_ids):
        raise RuntimeError("unexpected observation row count")
    if lineage_count != len(expected_observation_ids):
        raise RuntimeError("unexpected lineage row count")
    if pit_violations != 0:
        raise RuntimeError("PIT availability violation")
    return {
        "raw_count": raw_count,
        "observation_count": observation_count,
        "lineage_count": lineage_count,
        "pit_violations": pit_violations,
    }


def main() -> None:
    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        raise RuntimeError("FRED_API_KEY runtime secret is required")

    coinbase_result, coinbase_raw, coinbase_rows = _fetch_coinbase()
    fred2_result, fred2_raw, fred2_rows = _fetch_fred("DGS2", api_key)
    fred10_result, fred10_raw, fred10_rows = _fetch_fred("DGS10", api_key)

    if not coinbase_rows or not fred2_rows or not fred10_rows:
        raise RuntimeError("each approved source must produce at least one observation")

    bundles = [
        (coinbase_raw, coinbase_rows),
        (fred2_raw, fred2_rows),
        (fred10_raw, fred10_rows),
    ]

    with psycopg.connect() as conn:
        _seed_sources(conn)
        for raw, rows in bundles:
            _persist(conn, raw, rows)
        # Repeat the same exact rows to prove deterministic idempotency by primary key.
        for raw, rows in bundles:
            _persist(conn, raw, rows)

        raw_ids = {raw.raw_event_id for raw, _ in bundles}
        observation_ids = {row.observation_id for _, rows in bundles for row in rows}
        counts = _verify(conn, raw_ids, observation_ids)

    summary = {
        "status": "success",
        "database": "ephemeral-ci-only",
        "persistent_live_ingestion": False,
        "coinbase": {
            "http_status": coinbase_result.evidence.status,
            "safe_url": coinbase_result.evidence.safe_url,
            "sha256": coinbase_result.evidence.sha256_hex,
            "observations": len(coinbase_rows),
        },
        "fred_dgs2": {
            "http_status": fred2_result.evidence.status,
            "safe_url": fred2_result.evidence.safe_url,
            "sha256": fred2_result.evidence.sha256_hex,
            "observations": len(fred2_rows),
        },
        "fred_dgs10": {
            "http_status": fred10_result.evidence.status,
            "safe_url": fred10_result.evidence.safe_url,
            "sha256": fred10_result.evidence.sha256_hex,
            "observations": len(fred10_rows),
        },
        "postgres": counts,
    }
    encoded = json.dumps(summary, sort_keys=True)
    if api_key in encoded:
        raise RuntimeError("secret appeared in dry-run summary")
    print(encoded)


if __name__ == "__main__":
    main()
