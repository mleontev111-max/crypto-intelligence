import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapters.fred_h15_treasury import build_url, parse_observations, safe_request_metadata, raw_record_metadata  # noqa: E402


class FredH15AdapterTest(unittest.TestCase):
    def test_only_approved_series(self):
        url = build_url(series_id="DGS10", api_key="runtime-placeholder", realtime_start="2026-09-01", realtime_end="2026-09-01")
        self.assertIn("series_id=DGS10", url)
        with self.assertRaises(ValueError):
            build_url(series_id="VIXCLS", api_key="x", realtime_start="2026-09-01", realtime_end="2026-09-01")

    def test_secret_not_in_safe_metadata(self):
        meta = safe_request_metadata(series_id="DGS2", realtime_start="2026-09-01", realtime_end="2026-09-01")
        self.assertNotIn("api_key", meta)

    def test_missing_value_preserved(self):
        payload = {"observations": [{"realtime_start":"2026-09-01","realtime_end":"2026-09-01","date":"2026-08-31","value":"."}]}
        rows = parse_observations(payload)
        self.assertIsNone(rows[0]["value"])

    def test_available_at_is_first_seen(self):
        meta = raw_record_metadata(observed_at="2026-09-04T12:00:00Z", ingested_at="2026-09-04T12:00:01Z", content_hash="sha256:abcdef0123456789")
        self.assertEqual(meta["available_at"], "2026-09-04T12:00:00Z")


if __name__ == "__main__":
    unittest.main()
