# Phase 0 Checkpoint — Single-Node Manual Runtime Verified

Date: 2026-09-04
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Package and validate the simplest persistent single-node runtime for Crypto Intelligence without enabling scheduled ingestion.

## SUMMARIZED STATE SHA

`62fc738d69845fb4bc722a300bde6b290d2e11fc`

This is the exact implementation state summarized by this checkpoint. Checkpoint/pointer-only commits may be descendants.

## WHAT CHANGED

- Added `requirements-runtime.txt` with only the PostgreSQL Python client needed by the collector.
- Added a minimal Python 3.12 collector `Dockerfile`.
- Added `compose.yml` with:
  - PostgreSQL 16 persisted in `postgres_data`;
  - collector RAW bytes persisted in `raw_data`;
  - `migrate` and `collector` behind the `manual` Compose profile;
  - normal `docker compose up -d db` starts the database only;
  - no scheduler or background collector service.
- Added `.env.example` for the four runtime variables: PostgreSQL DB/user/password and FRED API key.
- Added `docs/operations/SINGLE_NODE_RUNTIME_v0.1.md` with explicit start, migrate, disabled-check, manual-collection, inspect, and stop commands.
- Added `Single-Node Runtime Guard` to validate the package using disposable CI volumes.
- First runtime guard reached real collection successfully but failed in the final shell verification because of nested quoting in a SQL command substitution; the verification script was simplified and rerun.

## VERIFIED

Single-Node Runtime Guard run #2 on summarized state SHA: SUCCESS.

Verified sequence:
- Compose model parses: PASS;
- collector Docker image builds: PASS;
- `docker compose up -d db` starts only `db`: PASS;
- PostgreSQL becomes healthy: PASS;
- manual `migrate` service applies Phase 0 migrations: PASS;
- manual collector with no arguments returns disabled/no-network/no-write state: PASS;
- one bounded real Coinbase/FRED collection through the Compose collector: PASS;
- database verification: 3 RAW rows, 30 observations, 30 lineage rows, 3 `file://` RAW references: PASS;
- persistent RAW volume contains exactly 3 `.bin` responses: PASS;
- `PROJECT_STATE.live_ingestion_allowed` remains false: PASS;
- teardown removes only the disposable CI volumes used by the test: PASS.

Phase 0 Contract Guard on the same summarized state SHA: SUCCESS.

## DECISIONS

- Single-node Docker Compose is the deployment shape for the first Market Observatory period.
- Keep PostgreSQL and local RAW storage on Docker volumes initially; no S3/R2, Timescale, Kubernetes, Kafka, Celery, or scheduler is required yet.
- Keep collector execution manual until a persistent-host run is verified.
- Public-source data do not justify additional secrecy/security layers beyond normal runtime secret handling and research-integrity provenance.
- The repo now contains enough deployment material to run one controlled persistent-host collection without further architecture work.

## UNKNOWN

- The runtime package has not yet been deployed on the selected persistent host.
- The actual host volume names/available disk and Docker Compose version have not yet been verified on that host.
- No persistent-host RAW files or database rows exist yet from this package.
- Regular collection cadence has not been selected or enabled.

## BLOCKERS

Code and CI are not blockers.

The only remaining Gate A blocker is one controlled manual run on the persistent host and verification that the host retains PostgreSQL and RAW volumes across container restart.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false` for regular/scheduled collection.
- Exactly one controlled persistent-host collection may be performed as the next validation gate; this does not authorize scheduling.
- No trading/execution.
- Only approved Coinbase BTC-USD candles and FRED DGS2/DGS10.
- FRED key must remain runtime-only in host `.env` and must not be pasted into GitHub/chat/logs.

## ONE NEXT ACTION

Deploy the validated `compose.yml` package on the selected persistent host, create the host `.env` locally (without committing it), start PostgreSQL, apply migrations, verify the collector is disabled by default, run exactly one bounded manual Coinbase/FRED collection, restart the database container, and verify that the 3 RAW files plus 3 RAW / 30 observation / 30 lineage database rows persist after restart; keep scheduling off and keep `live_ingestion_allowed=false` until the resulting host evidence is checkpointed.