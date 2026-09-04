# Phase 0 Contract Guard + PostgreSQL Mapping Checkpoint

**Date:** 2026-09-04  
**Phase:** 0 — Foundation  
**Status:** ACTIVE  
**Summarized state SHA:** `6508c2863442622e824aad984097e30a75461ec5`

## GOAL

Protect the new Phase 0 contracts from pointer/schema drift and define how logical contracts will map into PostgreSQL before any migration or ingestion is allowed.

## WHAT CHANGED

- Added `scripts/validate_phase0_contracts.py`.
- Added `.github/workflows/phase0-contract-guard.yml`.
- Added `docs/architecture/POSTGRESQL_MAPPING.md`.
- Guard checks canonical files, JSON syntax, PROJECT_STATE/CHECKPOINT_INDEX pointer agreement, non-empty ONE NEXT ACTION, Phase 0 safety flags and required schema fields.
- PostgreSQL mapping now defines proposed physical tables, provenance joins, keys, invariants, indexes and unresolved choices.

## VERIFIED

- `main` before this checkpoint contains the guard and mapping at `6508c2863442622e824aad984097e30a75461ec5`.
- Live trading remains forbidden.
- Live ingestion remains forbidden.
- Target definitions remain versioned and unresolved rather than guessed.
- PostgreSQL mapping does not create a database or migration.

## UNKNOWN

- GitHub Actions result for the new guard still needs verification on exact current main.
- UUID generation strategy is not selected.
- Numeric precision for price/return/probability is not finalized.
- TimescaleDB immediate-vs-deferred decision is not finalized.
- Append-only enforcement mechanism (permissions/triggers/application discipline) is not finalized.
- Quant research may change target/evaluation contracts before those layers become canonical.

## BLOCKERS

No blocker for validating the guard and drafting the first migration. Live ingestion remains intentionally blocked.

## DECISIONS

- Standard-library guard first; avoid extra CI dependencies during foundation.
- Physical schema must preserve the same PIT/provenance chain as JSON contracts.
- Forecast probabilities use a normalized child table rather than fixed DOWN/RANGE/UP columns.
- Target definitions live in a separate versioned table.
- TimescaleDB is a measured optimization, not an automatic dependency.

## FILES CHANGED

`scripts/validate_phase0_contracts.py`, `.github/workflows/phase0-contract-guard.yml`, `docs/architecture/POSTGRESQL_MAPPING.md`, this checkpoint.

## VALIDATION

Run `python scripts/validate_phase0_contracts.py` and verify the GitHub Actions `Phase 0 Contract Guard` result on exact current main.

## SAFETY BOUNDARIES

No live ingestion, no exchange credentials, no trading, no model promotion, no production database mutation.

## ONE NEXT ACTION

Verify the Phase 0 Contract Guard on exact main, then create the first reversible PostgreSQL migration and migration-validation test for the core provenance chain (`data_sources`, `raw_events`, `observations`, snapshot/model/target/forecast/outcome tables) without enabling live ingestion.