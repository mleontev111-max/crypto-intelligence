from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
import os
import unittest
from unittest.mock import patch

from scripts.collect_approved_sources import main


class CollectorDisabledTests(unittest.TestCase):
    def test_default_mode_does_not_require_runtime_configuration(self) -> None:
        output = StringIO()
        with patch.dict(os.environ, {}, clear=True), redirect_stdout(output):
            code = main([])
        self.assertEqual(code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "disabled")
        self.assertFalse(payload["network_fetch_performed"])
        self.assertFalse(payload["database_write_performed"])

    def test_write_mode_requires_raw_storage_before_network(self) -> None:
        with patch.dict(os.environ, {"FRED_API_KEY": "runtime-only"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "RAW_STORAGE_DIR"):
                main([
                    "--write",
                    "--coinbase-start", "2026-09-01T00:00:00Z",
                    "--coinbase-end", "2026-09-01T03:00:00Z",
                    "--fred-realtime-date", "2026-09-01",
                    "--fred-observation-start", "2026-08-25",
                    "--fred-observation-end", "2026-09-01",
                ])


if __name__ == "__main__":
    unittest.main()
