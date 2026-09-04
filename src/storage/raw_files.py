"""Minimal local content-addressed storage for immutable public-source RAW bytes."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import os
import tempfile


def store_raw_bytes(
    *,
    root: str | Path,
    body: bytes,
    expected_sha256: str | None = None,
) -> tuple[str, str]:
    if not isinstance(body, bytes):
        raise TypeError("body must be bytes")
    digest = sha256(body).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("RAW body hash does not match expected SHA-256")

    root_path = Path(root).expanduser().resolve()
    target_dir = root_path / digest[:2]
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{digest}.bin"

    if not target.exists():
        fd, temp_name = tempfile.mkstemp(prefix=f".{digest}.", dir=target_dir)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    else:
        existing_digest = sha256(target.read_bytes()).hexdigest()
        if existing_digest != digest:
            raise RuntimeError("existing RAW file content does not match its content-addressed name")

    return digest, target.as_uri()
