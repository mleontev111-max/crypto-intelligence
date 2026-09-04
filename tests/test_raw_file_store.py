from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from src.storage.raw_files import store_raw_bytes


class RawFileStoreTests(unittest.TestCase):
    def test_store_is_content_addressed_and_idempotent(self) -> None:
        body = b'{"hello":"world"}'
        digest = sha256(body).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            digest1, ref1 = store_raw_bytes(root=tmp, body=body, expected_sha256=digest)
            digest2, ref2 = store_raw_bytes(root=tmp, body=body, expected_sha256=digest)
            self.assertEqual(digest1, digest)
            self.assertEqual(digest2, digest)
            self.assertEqual(ref1, ref2)
            path = Path(ref1.removeprefix("file://"))
            self.assertTrue(path.exists())
            self.assertEqual(path.read_bytes(), body)

    def test_expected_hash_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                store_raw_bytes(root=tmp, body=b"abc", expected_sha256="0" * 64)


if __name__ == "__main__":
    unittest.main()
