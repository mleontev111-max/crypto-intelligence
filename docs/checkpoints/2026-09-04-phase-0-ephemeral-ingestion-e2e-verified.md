# Phase 0 Checkpoint — Ephemeral End-to-End Ingestion Verified

Date: 2026-09-04
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Verify the complete approved-source path end to end using real public source responses and a disposable PostgreSQL service, while keeping persistent live ingestion disabled.

## SUMMARIZED STATE SHA

`682bdadf3471e15aed8c6b59bbb4cb8f410fef64`

This is the exact implementation state summarized by this checkpoint. Checkpoint/pointer-only commits may be descendants.

## WHAT CHANGED

- Added bounded FRED observation windows so controlled probes do not retrieve the full historical series unnecessarily.
- Extended FRED request identity to include bounded observation dates.
- Added `scripts/e2e_approved_ingestion_dry_run.py` using the existing read-only transport, approved adapters, minimal ingestion mapping, and ordinary PostgreSQL transactions.
- Added `.github/workflows/ephemeral-ingestion-dry-run.yml` with PostgreSQL 16, runtime FRED secret, migrations, real source fetches, DB writes, idempotency verification, PIT verification, and disposable teardown.
- Fixed the workflow Python import path after the first run failed before source fetch due to `ModuleNotFoundError: src`.

## VERIFIED

Ephemeral Ingestion Dry Run run #2 on summarized state SHA: SUCCESS.

Real source results:
- Coinbase BTC-USD fixed historical 1h window: HTTP 200, 4 candles -> 20 OHLCV observations, SHA-256 `7dadbe88f945b05467a3232c471859175ef0b018202f427b0ccc4666d1340640`.
- FRED DGS2 bounded window 2026-08-25..2026-09-01 at realtime date 2026-09-01: HTTP 200, 5 numeric observations, SHA-256 `245afda8c6a913923b54b1e69c8d2b7fd6620d239b7f9755138069acd71c74c9`.
- FRED DGS10 same bounded window: HTTP 200, 5 numeric observations, SHA-256 `827e73b168fd3222c4ba5a5ab3a3a16f81f6d317c3893b65be96f6cf672da418`.
- FRED URLs in logs contained `api_key=REDACTED`; the key value was not printed.

Ephemeral PostgreSQL verification:
- RAW rows: 3
- observations: 30
- lineage rows: 30
- PIT violations (`observation.available_at < raw.available_at`): 0
- exact same bundles were written twice; deterministic primary keys prevented duplicates.
- final workflow check confirmed `PROJECT_STATE.live_ingestion_allowed == false`.
- PostgreSQL service container was removed at job teardown.

## DECISIONS

- Gate A technical proof is complete: approved public data can travel through fetch -> adapter -> RAW/observation mapping -> PostgreSQL and remain reproducible/idempotent.
- Do not add more defensive DB machinery for these public data sources unless a measured need appears.
- Keep production/persistent ingestion off until the runtime target and RAW payload storage location are explicit.
- Before enabling regular collection, preserve exact response bytes outside transient process memory using a simple content-addressed RAW store; `raw_events.payload_ref` must point to that stored object rather than only a conceptual hash reference.

## UNKNOWN

- Persistent PostgreSQL runtime endpoint/credentials for the application have not been wired to the collector.
- Persistent RAW byte storage path has not been implemented.
- Collector schedule/cadence is not active.
- No production database writes have occurred.

## BLOCKERS

No technical blocker to implementing the persistent collector in disabled-by-default mode.

Persistent collection should not be activated until RAW bytes are actually stored and the target PostgreSQL instance/storage volume are configured.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false` remains unchanged.
- No trading/execution.
- Only approved Coinbase BTC-USD and FRED DGS2/DGS10 sources are in scope.
- FRED API key remains runtime-only.

## ONE NEXT ACTION

Implement the minimal persistent collector in disabled-by-default mode: write exact response bytes to a local content-addressed RAW directory (`RAW_STORAGE_DIR`) keyed by SHA-256, use that immutable file reference in `raw_events.payload_ref`, write RAW + observations + lineage to a PostgreSQL connection supplied by runtime configuration, and add deterministic tests plus an ephemeral integration test; do not schedule or activate regular collection yet and keep `live_ingestion_allowed=false`.