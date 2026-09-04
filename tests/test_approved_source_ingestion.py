from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.ingestion.approved_sources import (
    coinbase_payload_to_rows,
    coinbase_request_record_id,
    fred_payload_to_rows,
    fred_request_record_id,
)


class ApprovedSourceIngestionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observed_at = datetime(2026, 9, 4, 12, 40, 56, tzinfo=timezone.utc)
        self.ingested_at = datetime(2026, 9, 4, 12, 41, 0, tzinfo=timezone.utc)

    def test_coinbase_maps_one_candle_to_five_observations(self) -> None:
        payload = [[1756684800, "107000", "109000", "108000", "108253.09", "12.5"]]
        raw, rows = coinbase_payload_to_rows(
            payload=payload,
            start="2026-09-01T00:00:00Z",
            end="2026-09-01T01:00:00Z",
            granularity=3600,
            observed_at=self.observed_at,
            ingested_at=self.ingested_at,
            content_hash="abc123",
            payload_ref="sha256:abc123",
        )
        self.assertEqual(raw.available_at, self.observed_at)
        self.assertEqual(len(rows), 5)
        self.assertEqual({row.metric_id for row in rows}, {
            "market.open", "market.high", "market.low", "market.close", "market.volume"
        })
        close = next(row for row in rows if row.metric_id == "market.close")
        self.assertEqual(str(close.value), "108253.09")
        self.assertEqual(close.asset, "BTC")
        self.assertEqual(close.venue, "coinbase")
        self.assertEqual(close.available_at, self.observed_at)

    def test_coinbase_mapping_is_deterministic_for_same_response_identity(self) -> None:
        kwargs = dict(
            payload=[[1756684800, "107000", "109000", "108000", "108253.09", "12.5"]],
            start="2026-09-01T00:00:00Z",
            end="2026-09-01T01:00:00Z",
            granularity=3600,
            observed_at=self.observed_at,
            ingested_at=self.ingested_at,
            content_hash="samehash",
            payload_ref="sha256:samehash",
        )
        raw1, rows1 = coinbase_payload_to_rows(**kwargs)
        raw2, rows2 = coinbase_payload_to_rows(**kwargs)
        self.assertEqual(raw1.raw_event_id, raw2.raw_event_id)
        self.assertEqual([r.observation_id for r in rows1], [r.observation_id for r in rows2])

    def test_fred_maps_numeric_rows_and_skips_dot_missing_value(self) -> None:
        payload = {
            "observations": [
                {"date": "2026-09-01", "realtime_start": "2026-09-01", "realtime_end": "2026-09-01", "value": "3.62"},
                {"date": "2026-09-02", "realtime_start": "2026-09-01", "realtime_end": "2026-09-01", "value": "."},
            ]
        }
        raw, rows = fred_payload_to_rows(
            payload=payload,
            series_id="DGS2",
            realtime_start="2026-09-01",
            realtime_end="2026-09-01",
            observed_at=self.observed_at,
            ingested_at=self.ingested_at,
            content_hash="fredhash",
            payload_ref="sha256:fredhash",
        )
        self.assertEqual(raw.available_at, self.observed_at)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].metric_id, "macro.fred.dgs2")
        self.assertEqual(rows[0].asset, "US_RATES")
        self.assertEqual(rows[0].unit, "percent")
        self.assertEqual(str(rows[0].value), "3.62")
        self.assertEqual(rows[0].available_at, self.observed_at)

    def test_request_record_ids_contain_no_secret_material(self) -> None:
        coinbase_id = coinbase_request_record_id(
            start="2026-09-01T00:00:00Z", end="2026-09-01T01:00:00Z", granularity=3600
        )
        fred_id = fred_request_record_id(
            series_id="DGS10", realtime_start="2026-09-01", realtime_end="2026-09-01"
        )
        self.assertIn("BTC-USD", coinbase_id)
        self.assertIn("DGS10", fred_id)
        self.assertNotIn("api_key", fred_id.lower())

    def test_fred_bad_date_rejected(self) -> None:
        payload = {
            "observations": [
                {"date": "not-a-date", "realtime_start": "2026-09-01", "realtime_end": "2026-09-01", "value": "3.62"}
            ]
        }
        with self.assertRaises(ValueError):
            fred_payload_to_rows(
                payload=payload,
                series_id="DGS10",
                realtime_start="2026-09-01",
                realtime_end="2026-09-01",
                observed_at=self.observed_at,
                ingested_at=self.ingested_at,
                content_hash="fredhash",
                payload_ref="sha256:fredhash",
            )


if __name__ == "__main__":
    unittest.main()
