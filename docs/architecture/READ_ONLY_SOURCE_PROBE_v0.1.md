# Read-Only Source Probe v0.1

**Status:** Canonical Phase 0 safety contract.  
**Database writes:** forbidden.  
**Trading/account actions:** forbidden.

## Purpose

Verify real provider connectivity and response semantics before designing any ingestion transaction. A probe may fetch approved read-only data and emit sanitized evidence, but it may not persist RAW rows, observations, credentials, or trading/account data.

## Allowed hosts

- `api.exchange.coinbase.com`
- `api.stlouisfed.org`

Transport rejects non-HTTPS URLs, unapproved hosts, URL userinfo, unbounded retry counts, and non-GET behavior.

## Evidence contract

A successful probe may emit only:

- sanitized URL with secret query values redacted;
- request/receive timestamps;
- HTTP status;
- content type;
- response byte length;
- SHA-256 of exact response bytes;
- bounded attempt count;
- parsed record count and source/series identity.

Raw response bytes remain in process memory only during Phase 0 probe execution and are not written to PostgreSQL or committed to GitHub.

## Retry and timeout boundary

- explicit positive timeout;
- maximum 5 attempts in transport, default 3;
- retries limited to network errors and HTTP 429/500/502/503/504;
- bounded exponential delay;
- no infinite retry loop.

## Secret boundary

FRED API key is read from runtime environment only. Query-string secret values are redacted before evidence metadata is emitted. Static CI checks reject committed credential-like literals in adapter/transport/probe code.

## Verified Coinbase live probe

Implementation commit: `e6a7672881890629e0fd843c96506a6483864038`.

GitHub Actions Market Adapter Guard performed a live zero-write Coinbase Exchange probe for fixed historical `BTC-USD` 1h candles (`2026-09-01T00:00:00Z` through `03:00:00Z`).

Observed evidence:

- HTTP status: `200`
- attempts: `1`
- parsed records: `4`
- response bytes: `242`
- content type: `application/json; charset=utf-8`
- SHA-256: `7dadbe88f945b05467a3232c471859175ef0b018202f427b0ccc4666d1340640`

No database/trading imports or literal credentials were present; deterministic adapter/transport tests passed before the live request.

## FRED live probe status

Not yet executed because no runtime `FRED_API_KEY` is configured for this repository workflow. This is an intentional safety blocker, not a reason to bypass the approved API contract with a different endpoint.

When the secret exists, the same zero-write probe must be run for both `DGS2` and `DGS10`; logs/evidence must contain only the redacted URL and safe metadata above.

## Gate after probes

Even after both Coinbase and FRED live probes succeed, `live_ingestion_allowed` remains `false`. The next layer is a separately reviewed PostgreSQL ingestion transaction with idempotency, RAW-first persistence, source-response lineage, failure atomicity and integration tests in a disposable database.