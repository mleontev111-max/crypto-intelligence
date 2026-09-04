import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapters.coinbase_exchange_candles import (  # noqa: E402
    BASE_URL,
    build_url,
    parse_candles,
    raw_record_metadata,
)


class CoinbaseExchangeCandleAdapterTest(unittest.TestCase):
    def test_builds_only_approved_btcusd_candle_url(self):
        url = build_url(
            start="2026-09-01T00:00:00Z",
            end="2026-09-02T00:00:00Z",
            granularity=3600,
        )
        self.assertTrue(url.startswith(BASE_URL + "?"))
        self.assertIn("granularity=3600", url)
        self.assertIn("BTC-USD", url)
        self.assertNotIn("orders", url)
        self.assertNotIn("accounts", url)

    def test_rejects_unapproved_granularity(self):
        with self.assertRaises(ValueError):
            build_url(start="a", end="b", granularity=14400)

    def test_parses_valid_fixture_shape(self):
        payload = [
            [1756684800, 108000.0, 111000.0, 109000.0, 110500.0, 123.45],
            [1756688400, 110000.0, 112000.0, 110500.0, 111500.0, 98.7],
        ]
        candles = parse_candles(payload)
        self.assertEqual(len(candles), 2)
        self.assertEqual(candles[0].source_event_at_seconds, 1756684800)

    def test_rejects_invalid_ohlc(self):
        with self.assertRaises(ValueError):
            parse_candles([[1756684800, 111000.0, 110000.0, 109000.0, 110500.0, 1.0]])

    def test_rejects_duplicate_timestamp(self):
        row = [1756684800, 108000.0, 111000.0, 109000.0, 110500.0, 1.0]
        with self.assertRaises(ValueError):
            parse_candles([row, row])

    def test_available_at_is_not_backdated_to_market_event(self):
        meta = raw_record_metadata(
            observed_at="2026-09-04T12:00:00Z",
            ingested_at="2026-09-04T12:00:01Z",
            content_hash="sha256:0123456789abcdef",
        )
        self.assertEqual(meta["available_at"], "2026-09-04T12:00:00Z")
        self.assertNotIn("source_event_at", meta)


if __name__ == "__main__":
    unittest.main()
