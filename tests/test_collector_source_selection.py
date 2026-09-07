from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch

from scripts.collect_approved_sources import main


class CollectorSourceSelectionTests(unittest.TestCase):
    """--sources lets a bounded run collect only one approved source.

    Default behavior (no --sources, i.e. "all") is unchanged and stays
    covered by tests/test_collector_disabled.py; these tests only cover
    the new selective-source argument validation.
    """

    def test_fred_only_does_not_require_coinbase_window(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            with patch.dict(
                os.environ,
                {"RAW_STORAGE_DIR": raw_dir, "FRED_API_KEY": "runtime-only"},
                clear=True,
            ):
                with self.assertRaisesRegex(RuntimeError, "--fred-realtime-date"):
                    main(["--write", "--sources", "fred"])

    def test_coinbase_only_does_not_require_fred_key_or_window(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            with patch.dict(os.environ, {"RAW_STORAGE_DIR": raw_dir}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "--coinbase-start"):
                    main(["--write", "--sources", "coinbase"])

    def test_all_still_requires_every_argument(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            with patch.dict(
                os.environ,
                {"RAW_STORAGE_DIR": raw_dir, "FRED_API_KEY": "runtime-only"},
                clear=True,
            ):
                with self.assertRaisesRegex(RuntimeError, "--coinbase-start"):
                    main(["--write"])  # --sources omitted defaults to "all"


if __name__ == "__main__":
    unittest.main()
