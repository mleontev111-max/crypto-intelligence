from datetime import datetime, timezone
from decimal import Decimal
import unittest

from src.ingestion.raw_first import build_observation, build_raw_event

UTC = timezone.utc


class RawFirstIngestionTest(unittest.TestCase):
    def fixture_raw(self, *, content_hash: str = "hash-v1"):
        return build_raw_event(
            source_id="market.coinbase.exchange.btcusd.candles",
            source_record_id="coinbase:BTC-USD:3600:2026-09-01T00:00Z:2026-09-01T03:00Z",
            source_event_at=datetime(2026, 9, 1, 0, tzinfo=UTC),
            provider_published_at=None,
            observed_at=datetime(2026, 9, 4, 12, 40, 56, tzinfo=UTC),
            ingested_at=datetime(2026, 9, 4, 12, 41, tzinfo=UTC),
            available_at=datetime(2026, 9, 4, 12, 40, 56, tzinfo=UTC),
            content_hash=content_hash,
            payload_ref="fixture://coinbase-v1",
            mime_type="application/json",
        )

    def test_exact_repeat_has_same_raw_id(self):
        self.assertEqual(self.fixture_raw().raw_event_id, self.fixture_raw().raw_event_id)

    def test_changed_payload_hash_creates_revision_identity(self):
        self.assertNotEqual(
            self.fixture_raw(content_hash="hash-v1").raw_event_id,
            self.fixture_raw(content_hash="hash-v2").raw_event_id,
        )

    def test_observation_is_deterministic_and_linked_to_raw(self):
        raw = self.fixture_raw()
        kwargs = dict(
            raw=raw,
            metric_id="market.close",
            asset="BTC",
            venue="coinbase",
            value=Decimal("108253.09"),
            unit="USD",
            event_at=datetime(2026, 9, 1, 0, tzinfo=UTC),
            available_at=raw.available_at,
            quality_status="valid",
            normalizer_version="coinbase-candles-v0.1",
        )
        left = build_observation(**kwargs)
        right = build_observation(**kwargs)
        self.assertEqual(left.observation_id, right.observation_id)
        self.assertEqual(left.raw_event_id, raw.raw_event_id)

    def test_observation_cannot_predate_raw_availability(self):
        raw = self.fixture_raw()
        with self.assertRaises(ValueError):
            build_observation(
                raw=raw,
                metric_id="market.close",
                asset="BTC",
                venue="coinbase",
                value=Decimal("108253.09"),
                unit="USD",
                event_at=datetime(2026, 9, 1, 0, tzinfo=UTC),
                available_at=datetime(2026, 9, 4, 12, 40, 55, tzinfo=UTC),
                quality_status="valid",
                normalizer_version="coinbase-candles-v0.1",
            )

    def test_raw_available_at_cannot_be_after_ingestion(self):
        with self.assertRaises(ValueError):
            build_raw_event(
                source_id="macro.fred.h15.dgs2_dgs10",
                source_record_id="fred:DGS2:2026-09-01",
                source_event_at=datetime(2026, 9, 1, tzinfo=UTC),
                provider_published_at=None,
                observed_at=datetime(2026, 9, 4, 12, tzinfo=UTC),
                ingested_at=datetime(2026, 9, 4, 12, 0, 1, tzinfo=UTC),
                available_at=datetime(2026, 9, 4, 12, 0, 2, tzinfo=UTC),
                content_hash="hash",
                payload_ref="fixture://fred",
            )


if __name__ == "__main__":
    unittest.main()
