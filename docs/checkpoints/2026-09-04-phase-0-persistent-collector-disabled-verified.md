# Phase 0 Checkpoint — Disabled Persistent-Shaped Collector Verified

Date: 2026-09-04
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Implement the minimal collector shape needed for persistent operation without activating regular collection: exact RAW bytes on disk, runtime PostgreSQL writes, explicit bounded source windows, and disabled-by-default execution.

## SUMMARIZED STATE SHA

`d995a869e2dc5e72d865c6f3f8c904cda3b69980`

This is the exact implementation state summarized by this checkpoint. Checkpoint/pointer-only commits may be descendants.

## WHAT CHANGED

- Added `src/storage/raw_files.py` for local content-addressed RAW storage: SHA-256 -> `<RAW_STORAGE_DIR>/<prefix>/<sha256>.bin`.
- Added deterministic RAW file-store tests for idempotent repeat storage and expected-hash mismatch rejection.
- Added `src/ingestion/postgres_writer.py` as a small reusable PostgreSQL writer using ordinary transactions and existing primary keys; no extra DB security machinery was added.
- Added `scripts/collect_approved_sources.py`.
  - Default mode performs no HTTP requests and no database writes.
  - `--write` is required for collection.
  - `--write` additionally requires explicit Coinbase/FRED windows, `RAW_STORAGE_DIR`, runtime `FRED_API_KEY`, and PostgreSQL configuration (`DATABASE_URL` or standard `PG*` variables).
  - Exact response bytes are stored before their `payload_ref` is written to `raw_events`.
  - FRED key is not included in request identities or summaries.
- Added tests proving default collector mode remains disabled without runtime configuration and write mode refuses to start when RAW storage configuration is absent.
- Updated the existing ephemeral ingestion workflow to execute this persistent-shaped collector twice against one disposable PostgreSQL database and one disposable RAW directory.
- First workflow definition failed before jobs because `runner.temp` was used in top-level workflow `env`; replaced it with the fixed ephemeral runner path `/tmp/crypto-intelligence-raw`.

## VERIFIED

Ephemeral Ingestion Dry Run run #5 on summarized state SHA: SUCCESS.

The workflow verified:
- collector disabled mode: PASS;
- RAW file-store deterministic tests: PASS;
- Phase 0 PostgreSQL schema application: PASS;
- persistent-shaped collector run #1: PASS;
- same collector run #2 against same database/storage: PASS;
- exactly 3 `.bin` RAW files after both runs;
- exactly 3 `raw_events` after both runs;
- all 3 `raw_events.payload_ref` values are `file://` references;
- exactly 30 observations;
- exactly 30 RAW->observation lineage rows;
- zero cases where observation `available_at` predates linked RAW `available_at`;
- every RAW filename SHA-256 matches its file contents;
- every database `content_hash` matches the bytes referenced by `payload_ref`;
- FRED secret remained runtime-only/redacted;
- `PROJECT_STATE.live_ingestion_allowed` remained false.

Phase 0 Contract Guard on the same summarized state SHA: SUCCESS.

## DECISIONS

- The collector is now production-shaped but operationally disabled by default.
- Keep the implementation simple because the source data are public; the guarantees are for research integrity and reproducibility, not secrecy.
- Local content-addressed files are sufficient for the first single-node deployment; S3/R2 is deferred until scale/operations justify it.
- Ordinary PostgreSQL transactions and deterministic primary keys remain the idempotency/atomicity mechanism.
- Do not add a scheduler yet.
- Do not flip `live_ingestion_allowed` until the actual persistent single-node runtime is defined and a manual controlled run is explicitly accepted.

## UNKNOWN

- The actual persistent PostgreSQL service/volume for Crypto Intelligence has not yet been defined in deployment configuration.
- The persistent host path/volume for `RAW_STORAGE_DIR` has not yet been defined in deployment configuration.
- No persistent manual collection has run outside disposable CI.
- No collection cadence/scheduler has been activated.

## BLOCKERS

There is no code-level blocker to preparing the single-node runtime package.

Actual persistent collection remains blocked only by the deployment target/configuration gate.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false`.
- No scheduler.
- No trading/execution.
- Only Coinbase BTC-USD candles and FRED DGS2/DGS10 are approved in this path.
- FRED API key remains runtime-only.

## ONE NEXT ACTION

Prepare and validate a minimal single-node Docker runtime package for Crypto Intelligence: PostgreSQL 16 with a persistent volume, a persistent local RAW volume mapped to `RAW_STORAGE_DIR`, migration/bootstrap command, and the collector as a manual-only command with no scheduler; validate the package in CI using temporary volumes, document the exact runtime variables and manual collection command, and keep `live_ingestion_allowed=false` until a later checkpoint explicitly accepts one controlled persistent-host collection.