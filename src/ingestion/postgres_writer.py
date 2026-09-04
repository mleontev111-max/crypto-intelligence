"""Minimal PostgreSQL writer for RAW -> observations -> lineage bundles.

The connection object is supplied by the runtime. This module has no network source
logic and intentionally relies only on ordinary transactions and primary-key idempotency.
"""

from __future__ import annotations


def seed_approved_sources(conn) -> None:
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


def persist_bundle(conn, raw, observations) -> None:
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
