# Phase 0 Checkpoint — Fixture-Driven RAW-First Ingestion Verified

Date: 2026-09-04
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Close the fixture-driven RAW-first ingestion gate with the simplest design that preserves research integrity, then authorize only a disposable end-to-end live-source dry run in CI. Persistent live ingestion remains disabled.

## SUMMARIZED STATE SHA

`1109eb52924b548352456dfb54bc726cad099262`

This is the exact implementation state summarized by this checkpoint. Checkpoint/pointer-only commits may be descendants.

## WHAT CHANGED

- Added minimal deterministic RAW-first row builders in `src/ingestion/raw_first.py`.
- Added adapter-to-ingestion mapping for approved Coinbase BTC-USD candles and FRED DGS2/DGS10 in `src/ingestion/approved_sources.py`.
- Added deterministic/unit tests for RAW IDs, observation IDs, PIT-safe `available_at`, Coinbase OHLCV mapping, FRED mapping, missing FRED values, and secret-free request identities.
- Kept mapping modules free of HTTP and database clients.
- Extended PostgreSQL CI to verify a simple RAW -> observation -> lineage transaction, repeat insertion without duplicates, and rollback without partial RAW state.
- Removed an initially proposed heavier migration with additional DB functions/triggers after deciding that public-source ingestion should remain simple; existing RAW append-only protection plus ordinary PostgreSQL transactions are sufficient for Phase 0.

## VERIFIED

- PostgreSQL Migration Guard on `1100a82ca5209923e0dc190b4035684cf416397c`: SUCCESS.
  - deterministic RAW-first tests: PASS
  - core migrations: PASS
  - minimal RAW-first PostgreSQL transaction: PASS
  - repeated deterministic insert without duplicate IDs: PASS
  - failed observation insert rolls back partial RAW insert: PASS
  - existing core invariant tests: PASS
  - migration rollback/reapply: PASS
- Approved Source Ingestion Guard on `1109eb52924b548352456dfb54bc726cad099262`: SUCCESS.
  - RAW-first deterministic tests: PASS
  - Coinbase/FRED ingestion mapping tests: PASS
  - ingestion mapping remains network-free and DB-client-free: PASS

## DECISIONS

- Do not add security complexity for public market/macro data unless a concrete threat or operational need appears.
- Preserve only the minimum research-integrity guarantees: deterministic identity, RAW provenance, PIT-safe availability, lineage, ordinary transaction atomicity, and reproducibility.
- Persistent network -> database ingestion is still disabled.
- A disposable GitHub Actions PostgreSQL service may be used for a controlled end-to-end dry run because its database is ephemeral and destroyed after the job.
- The controlled dry run may fetch only already-approved public sources (Coinbase BTC-USD and FRED DGS2/DGS10), must redact the FRED secret, and must not persist results outside the ephemeral CI database/artifacts containing non-secret evidence.

## UNKNOWN

- End-to-end network -> adapter -> mapping -> PostgreSQL has not yet been exercised in one run.
- Persistent runtime database connection/configuration has not been selected or enabled.
- Regular collection cadence has not been activated.

## BLOCKERS

No blocker to an ephemeral CI-only end-to-end dry run.

Persistent live ingestion remains blocked until that dry run passes and a later checkpoint explicitly narrows the allowed persistent write path.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false` remains unchanged.
- No trading/execution.
- No exchange account credentials.
- FRED API key remains runtime-only and must never be printed or persisted.
- No broad source expansion in this gate.

## ONE NEXT ACTION

Implement and run one end-to-end GitHub Actions dry run that fetches a small fixed Coinbase BTC-USD historical candle window plus bounded FRED DGS2/DGS10 observations, maps them through the approved ingestion layer, writes RAW + observations + lineage into an ephemeral PostgreSQL 16 service inside one ordinary transaction per source response, verifies row counts/PIT timestamps/idempotent rerun/secret redaction, then destroys the database with the CI job; keep persistent live ingestion disabled and keep `live_ingestion_allowed=false`.