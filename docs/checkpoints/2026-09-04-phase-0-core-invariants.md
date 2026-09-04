# Phase 0 Core Database Invariants Checkpoint

**Date:** 2026-09-04  
**Phase:** 0 — Foundation  
**Status:** ACTIVE  
**Summarized state SHA:** `34798dee1e60f574d51f0f9068a2f6e6f850a191`

## GOAL

Enforce and test the critical cross-row point-in-time and forecast-integrity invariants before any live ingestion is allowed.

## WHAT CHANGED

- Added `db/migrations/0002_core_invariants.up.sql` and rollback migration.
- Enforced snapshot component cutoff: component `max_available_at` cannot exceed parent snapshot cutoff.
- Added deferred forecast probability-vector guard: at commit, each forecast must have at least two classes and probabilities must sum to 1 within fixed storage tolerance.
- Enforced forecast-outcome `target_definition_id` consistency with the parent forecast.
- Expanded PostgreSQL Migration Guard to test valid and invalid write paths, rollback, and re-apply.
- Recorded helper quant research as non-canonical research input in `docs/research/2026-09-04-helper-statistical-evaluation-v0.2.md`.

## VERIFIED

- PostgreSQL Migration Guard on implementation commit `b3937254e45a5db3a5a86f5fcbe6e0965dacc0aa`: SUCCESS.
- PostgreSQL 16 CI successfully applied migrations 0001 + 0002.
- CI seeded a valid minimal forecast chain successfully.
- CI correctly rejected a snapshot cutoff violation.
- CI correctly rejected forecast/outcome target mismatch.
- CI correctly rejected a probability vector summing to 1.1 at deferred commit time.
- CI rolled both migrations back, verified all 11 core tables were removed, and re-applied both migrations successfully.
- Phase 0 Contract Guard on summarized state `34798dee1e60f574d51f0f9068a2f6e6f850a191`: SUCCESS.
- Live ingestion, paper trading, and live trading remain disabled.

## UNKNOWN

- Final target semantics for DOWN/RANGE/UP remain research/open.
- Exact causal volatility estimator and thresholds remain open.
- Data-source providers, licensing/cost approval, and source-specific PIT/revision contracts are not yet approved for live collection.
- Forecast publication API/write service does not yet exist.
- Observation/raw ingestion service does not yet exist.

## BLOCKERS

No blocker for continuing Phase 0 design and source due diligence. Live ingestion remains blocked until at least one source is explicitly approved with licensing/access/PIT semantics and the ingestion write path is implemented/tested against these invariants.

## DECISIONS

- Critical provenance/publication invariants belong in the database, not only application code.
- Probability-vector validation is deferred to transaction commit so an atomic multi-row vector can be inserted safely.
- Research findings remain non-canonical until reviewed and promoted through a separate decision.
- No provider is considered approved merely because it appears in a candidate registry.

## FILES CHANGED

`db/migrations/0002_core_invariants.up.sql`, `db/migrations/0002_core_invariants.down.sql`, `.github/workflows/postgres-migration-guard.yml`, `docs/research/2026-09-04-helper-statistical-evaluation-v0.2.md`, this checkpoint.

## VALIDATION

- Phase 0 Contract Guard: SUCCESS on summarized state.
- PostgreSQL Migration Guard: SUCCESS on invariant implementation commit.

## SAFETY BOUNDARIES

No live ingestion, no external API credentials, no exchange order permissions, no paper portfolio execution, no model promotion, no production DB writes.

## ONE NEXT ACTION

Perform source-by-source Phase 0 due diligence for the BTC Market Observatory and commit an approval matrix covering access method, data semantics, point-in-time/revision behavior, licensing/terms, expected cadence, cost status, and exact first approved read-only dataset; do not enable ingestion until at least one source is explicitly approved and its adapter contract is defined.
