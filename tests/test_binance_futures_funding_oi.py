import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapters.binance_futures_funding_oi import (  # noqa: E402
    FUNDING_RATE_BASE_URL,
    OPEN_INTEREST_HIST_BASE_URL,
    build_funding_rate_url,
    build_open_interest_hist_url,
    parse_funding_rates,
    parse_open_interest_hist,
    raw_record_metadata,
)


class BinanceFundingRateAdapterTest(unittest.TestCase):
    def test_builds_only_approved_btcusdt_funding_rate_url(self):
        url = build_funding_rate_url(start_time_ms=1, end_time_ms=2, limit=1000)
        self.assertTrue(url.startswith(FUNDING_RATE_BASE_URL + "?"))
        self.assertIn("symbol=BTCUSDT", url)
        self.assertNotIn("order", url)
        self.assertNotIn("account", url)

    def test_rejects_funding_rate_limit_over_max(self):
        with self.assertRaises(ValueError):
            build_funding_rate_url(limit=1001)

    def test_parses_valid_funding_rate_fixture(self):
        payload = [
            {
                "symbol": "BTCUSDT",
                "fundingRate": "-0.03750000",
                "fundingTime": 1570608000000,
                "markPrice": "34287.54619963",
            }
        ]
        rows = parse_funding_rates(payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].source_event_at_ms, 1570608000000)

    def test_rejects_unapproved_symbol_in_funding_rate(self):
        with self.assertRaises(ValueError):
            parse_funding_rates([
                {"symbol": "ETHUSDT", "fundingRate": "0.0001", "fundingTime": 1}
            ])

    def test_rejects_duplicate_funding_time(self):
        row = {"symbol": "BTCUSDT", "fundingRate": "0.0001", "fundingTime": 1570608000000}
        with self.assertRaises(ValueError):
            parse_funding_rates([row, row])


class BinanceOpenInterestAdapterTest(unittest.TestCase):
    def test_builds_only_approved_btcusdt_open_interest_url(self):
        url = build_open_interest_hist_url(period="1h", limit=500)
        self.assertTrue(url.startswith(OPEN_INTEREST_HIST_BASE_URL + "?"))
        self.assertIn("symbol=BTCUSDT", url)
        self.assertIn("period=1h", url)

    def test_rejects_unapproved_period(self):
        with self.assertRaises(ValueError):
            build_open_interest_hist_url(period="3h")

    def test_rejects_open_interest_limit_over_max(self):
        with self.assertRaises(ValueError):
            build_open_interest_hist_url(limit=501)

    def test_parses_valid_open_interest_fixture(self):
        payload = [
            {
                "symbol": "BTCUSDT",
                "sumOpenInterest": "98666.163",
                "sumOpenInterestValue": "2236289208.197267",
                "timestamp": 1674259200000,
            }
        ]
        rows = parse_open_interest_hist(payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].source_event_at_ms, 1674259200000)

    def test_rejects_negative_open_interest(self):
        with self.assertRaises(ValueError):
            parse_open_interest_hist([
                {"symbol": "BTCUSDT", "sumOpenInterest": "-1", "timestamp": 1}
            ])


class RawRecordMetadataTest(unittest.TestCase):
    def test_available_at_is_not_backdated_to_market_event(self):
        meta = raw_record_metadata(
            dataset="open_interest_hist",
            observed_at="2026-09-06T12:00:00Z",
            ingested_at="2026-09-06T12:00:01Z",
            content_hash="sha256:0123456789abcdef",
        )
        self.assertEqual(meta["available_at"], "2026-09-06T12:00:00Z")
        self.assertNotIn("timestamp", meta)

    def test_rejects_unknown_dataset(self):
        with self.assertRaises(ValueError):
            raw_record_metadata(
                dataset="liquidations",
                observed_at="a",
                ingested_at="b",
                content_hash="c",
            )


if __name__ == "__main__":
    unittest.main()
