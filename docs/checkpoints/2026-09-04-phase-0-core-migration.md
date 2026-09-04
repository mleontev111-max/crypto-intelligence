# Phase 0 Core PostgreSQL Migration Checkpoint

**Date:** 2026-09-04  
**Phase:** 0 — Foundation  
**Status:** ACTIVE  
**Summarized state SHA:** `19933768b04d063b00ea1d94df6a60e6f5424397`

## GOAL

Create and validate the first reversible PostgreSQL migration for the core point-in-time provenance chain without enabling live ingestion.

## WHAT CHANGED

- Added `db/migrations/0001_core_provenance.up.sql`.
- Added `db/migrations/0001_core_provenance.down.sql`.
- Added `.github/workflows/postgres-migration-guard.yml` using PostgreSQL 16.
- Added `docs/architecture/POSTGRESQL_DECISIONS_v0.1.md`.
- Migration creates core source/RAW/observation/snapshot/model/target/forecast/outcome tables and key indexes.
- Append-only database triggers reject UPDATE/DELETE on scientific-evidence tables.
- TimescaleDB is explicitly deferred.
- Database IDs are stored as UUID without extension dependency; application-generated UUIDv7 is preferred when supported.
- Numeric precision choices are documented as engineering choices, not model-accuracy claims.

## VERIFIED

- Phase 0 Contract Guard on exact `dc44c87092ac40dbf20563b0309f578f5e1148bf`: SUCCESS.
- PostgreSQL Migration Guard on implementation commit `6bae56b7b3e24591cf2e402efc4b188a36a2a24c`: SUCCESS.
- PostgreSQL 16 CI successfully applied migration 0001, verified all 11 core tables, verified append-only trigger presence, rolled migration back, verified core tables were removed, and re-applied the migration.
- Phase 0 Contract Guard on summarized state `19933768b04d063b00ea1d94df6a60e6f5424397`: SUCCESS.
- Live trading remains forbidden.
- Paper trading remains forbidden.
- Live ingestion remains forbidden.

## UNKNOWN

- Cross-row probability-vector sum-to-one is not yet enforced by the database.
- `data_snapshot_components.max_available_at <= data_snapshots.cutoff_available_at` is not yet enforced by database trigger.
- Outcome target-definition equality with the parent forecast is not yet enforced by database trigger.
- Final `DOWN / RANGE / UP` target semantics remain research/open.
- Empirical evidence may later justify changing numeric precision or adding TimescaleDB.

## BLOCKERS

Live ingestion remains blocked until the critical cross-row point-in-time/publication invariants are enforced and tested.

## DECISIONS

- Plain PostgreSQL first; TimescaleDB deferred until measured need.
- Database-level append-only protection is required for scientific evidence.
- No database UUID extension dependency in migration 0001.
- Probability vector is normalized into child rows; aggregate sum-to-one requires a later atomic publication invariant.
- Research findings do not silently mutate target contracts; `target_definition_id` remains versioned.

## FILES CHANGED

`db/migrations/0001_core_provenance.up.sql`, `db/migrations/0001_core_provenance.down.sql`, `.github/workflows/postgres-migration-guard.yml`, `docs/architecture/POSTGRESQL_DECISIONS_v0.1.md`, this checkpoint.

## VALIDATION

- Phase 0 Contract Guard: SUCCESS on summarized state.
- PostgreSQL Migration Guard: SUCCESS on migration/workflow implementation commit.

## SAFETY BOUNDARIES

No live ingestion, no exchange credentials, no order execution, no paper portfolio, no model promotion, and no production database mutation.

## ONE NEXT ACTION

Add and test the critical database/write-path invariants for snapshot cutoff, forecast probability publication, and forecast-outcome target consistency; keep live ingestion disabled until these invariants are enforced and the PostgreSQL Migration Guard passes again.
