"""Constrained read-only HTTP transport for approved Phase 0 source probes.

This module knows nothing about PostgreSQL and exposes GET only. It returns raw bytes
plus sanitized evidence metadata suitable for a dry-run probe. Secrets in query strings
are redacted from evidence before any caller can persist or log the URL.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ALLOWED_HOSTS = {"api.exchange.coinbase.com", "api.stlouisfed.org"}
SECRET_QUERY_KEYS = {"api_key", "key", "secret", "token"}
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


@dataclass(frozen=True)
class ReadOnlyEvidence:
    requested_at: str
    received_at: str
    status: int
    safe_url: str
    content_type: str | None
    content_length: int
    sha256_hex: str
    attempts: int


@dataclass(frozen=True)
class ReadOnlyResult:
    body: bytes
    evidence: ReadOnlyEvidence


def sanitize_url(url: str) -> str:
    parts = urlsplit(url)
    safe_query = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        safe_query.append((key, "REDACTED" if key.lower() in SECRET_QUERY_KEYS else value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(safe_query), ""))


def _validate_url(url: str) -> None:
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise ValueError("only HTTPS GET is allowed")
    if parts.hostname not in ALLOWED_HOSTS:
        raise ValueError("host is not approved for Phase 0 probe")
    if parts.username or parts.password:
        raise ValueError("userinfo in URL is forbidden")


def read_only_get(
    url: str,
    *,
    timeout_seconds: float = 10.0,
    max_attempts: int = 3,
    opener: Callable = urlopen,
    sleeper: Callable[[float], None] = time.sleep,
) -> ReadOnlyResult:
    _validate_url(url)
    if timeout_seconds <= 0:
        raise ValueError("timeout must be positive")
    if not 1 <= max_attempts <= 5:
        raise ValueError("max_attempts must be between 1 and 5")

    requested_at = datetime.now(timezone.utc).isoformat()
    safe_url = sanitize_url(url)
    request = Request(url, method="GET", headers={"User-Agent": "crypto-intelligence-phase0-probe/0.1"})

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with opener(request, timeout=timeout_seconds) as response:
                status = int(response.getcode())
                body = response.read()
                received_at = datetime.now(timezone.utc).isoformat()
                content_type = response.headers.get("Content-Type") if response.headers else None
                return ReadOnlyResult(
                    body=body,
                    evidence=ReadOnlyEvidence(
                        requested_at=requested_at,
                        received_at=received_at,
                        status=status,
                        safe_url=safe_url,
                        content_type=content_type,
                        content_length=len(body),
                        sha256_hex=sha256(body).hexdigest(),
                        attempts=attempt,
                    ),
                )
        except HTTPError as exc:
            last_error = exc
            if exc.code not in RETRYABLE_STATUS or attempt == max_attempts:
                raise
        except URLError as exc:
            last_error = exc
            if attempt == max_attempts:
                raise

        sleeper(min(2 ** (attempt - 1), 4))

    raise RuntimeError("unreachable read-only HTTP retry state") from last_error
