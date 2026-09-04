# Phase 0 Data Contracts Checkpoint

**Date:** 2026-09-04  
**Phase:** 0 — Foundation  
**Status:** ACTIVE  
**Summarized state SHA:** `ef72668156ab06b82b0620ae52f51e03bd87dab0`

## GOAL

Complete the previously recorded ONE NEXT ACTION: define a Phase 0 data-source registry and canonical logical contracts for raw evidence, normalized observations, point-in-time snapshots, model versions, forecasts and outcomes without beginning live ingestion.

## WHAT CHANGED

- Added `docs/architecture/DATA_SOURCE_REGISTRY.md` with required provenance/PIT/licensing fields and candidate source families.
- Added `schemas/raw-event.schema.json`.
- Added `schemas/observation.schema.json`.
- Added `schemas/data-snapshot.schema.json`.
- Added `schemas/model-version.schema.json`.
- Added `schemas/forecast.schema.json`.
- Added `schemas/outcome.schema.json`.
- Added `docs/architecture/CANONICAL_DATA_CONTRACTS.md` tying the schemas into one immutable point-in-time chain.

## VERIFIED

- Current scope remains BTC only.
- Planned horizons remain 4h / 24h / 7d.
- No live ingestion, exchange credential, trading or portfolio write was introduced.
- Forecast schema references a versioned `target_definition_id`; no arbitrary DOWN/RANGE/UP threshold was embedded.
- Forecasts reference exact `model_version_id` and `data_snapshot_id`.
- Outcomes are separate from forecasts and resolve against the same target definition.
- `available_at` remains the controlling timestamp for point-in-time safety.

## UNKNOWN

- Exact target definitions for DOWN/RANGE/UP are pending quant research.
- Exact provider endpoints, commercial terms, rate limits and historical revision behavior are not approved yet.
- PostgreSQL/Timescale physical schema and migrations do not exist yet.
- Cross-record/application validation is specified conceptually but not automated yet.
- Evaluation/calibration protocol is still research input, not canonical policy.

## BLOCKERS

None for continuing Phase 0 foundation work.

## DECISIONS

- A data source stays `candidate` until timestamp/revision/licensing/security/freshness behavior is reviewed.
- Provider revisions must not rewrite the state that was available to a historical forecast.
- DataSnapshot is a manifest, not a duplicate copy of all data.
- Target semantics are versioned separately from Forecast records.
- JSON Schema defines logical contracts; database constraints and cross-record invariants will be implemented separately.

## FILES CHANGED

`docs/architecture/DATA_SOURCE_REGISTRY.md`, `docs/architecture/CANONICAL_DATA_CONTRACTS.md`, `schemas/raw-event.schema.json`, `schemas/observation.schema.json`, `schemas/data-snapshot.schema.json`, `schemas/model-version.schema.json`, `schemas/forecast.schema.json`, `schemas/outcome.schema.json`, this checkpoint.

## VALIDATION

The files were created on canonical `main`; the summarized state is commit `ef72668156ab06b82b0620ae52f51e03bd87dab0`. Pointer-only checkpoint/state commits may be descendants of that SHA.

## SAFETY BOUNDARIES

Architecture and contracts only. No live data collection. No exchange writes. No real-money execution. No model promotion.

## ONE NEXT ACTION

Add an automated Phase 0 contract/state guard that validates JSON syntax, required canonical files, checkpoint pointer agreement, non-empty ONE NEXT ACTION, and basic schema invariants; then define the PostgreSQL logical-to-physical mapping without starting live ingestion.