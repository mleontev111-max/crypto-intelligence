import io
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transport.read_only_http import read_only_get, sanitize_url  # noqa: E402


class FakeResponse:
    def __init__(self, body=b'{}', status=200, content_type='application/json'):
        self._body = body
        self._status = status
        self.headers = {'Content-Type': content_type}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def getcode(self):
        return self._status

    def read(self):
        return self._body


class ReadOnlyHttpTest(unittest.TestCase):
    def test_rejects_unapproved_host(self):
        with self.assertRaises(ValueError):
            read_only_get('https://example.com/data', opener=lambda *a, **k: FakeResponse())

    def test_rejects_plain_http(self):
        with self.assertRaises(ValueError):
            read_only_get('http://api.exchange.coinbase.com/products/BTC-USD/candles', opener=lambda *a, **k: FakeResponse())

    def test_redacts_fred_api_key_from_evidence(self):
        url = 'https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key=supersecret123&file_type=json'
        safe = sanitize_url(url)
        self.assertNotIn('supersecret123', safe)
        self.assertIn('api_key=REDACTED', safe)

    def test_hashes_raw_response_and_uses_get(self):
        captured = {}

        def opener(request, timeout):
            captured['method'] = request.get_method()
            captured['timeout'] = timeout
            return FakeResponse(body=b'[1,2,3]')

        result = read_only_get(
            'https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600',
            opener=opener,
            sleeper=lambda _: None,
        )
        self.assertEqual(captured['method'], 'GET')
        self.assertEqual(captured['timeout'], 10.0)
        self.assertEqual(result.evidence.status, 200)
        self.assertEqual(result.evidence.content_length, 7)
        self.assertEqual(len(result.evidence.sha256_hex), 64)
        self.assertEqual(result.body, b'[1,2,3]')

    def test_attempt_limit_is_bounded(self):
        with self.assertRaises(ValueError):
            read_only_get('https://api.exchange.coinbase.com/', max_attempts=99, opener=lambda *a, **k: FakeResponse())


if __name__ == '__main__':
    unittest.main()
