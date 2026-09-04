# Phase 0 Bootstrap Checkpoint

**Date:** 2026-09-04  
**Phase:** 0 — Foundation  
**Status:** ACTIVE  
**Summarized state SHA:** `09f27b375bec76bdc8cd4370352fe8cea54cdd13`

## GOAL

Bootstrap Crypto Intelligence as a durable GitHub-first project with enough canonical documentation that a new human or AI can resume without relying on the originating chat.

## WHAT CHANGED

- Established `START_HERE.md` resume/end-of-session protocol.
- Established contributor rules in `AGENTS.md`.
- Established project safety/methodology constitution.
- Added machine-readable `PROJECT_STATE.json` and `CHECKPOINT_INDEX.json`.
- Defined roadmap phases 0-6.
- Defined system architecture and point-in-time rule.
- Defined RAW/NORMALIZED/DERIVED data architecture.
- Defined immutable Forecast Ledger.
- Defined champion/challenger model lifecycle.
- Defined BTC-only MVP scope and exclusions.

## VERIFIED

- Repository exists at `mleontev111-max/crypto-intelligence` and is private.
- Default branch is `main`.
- Phase 0 architecture/state commit is `09f27b375bec76bdc8cd4370352fe8cea54cdd13`.
- Canonical project-state pointer and checkpoint-index pointer both target this checkpoint.

## UNKNOWN

- Exact external data providers and licensing/cost choices are not selected yet.
- Canonical database schemas are not yet committed.
- Hosting/deployment target is not selected.
- No ingestion reliability or model quality claims exist yet.

## BLOCKERS

None for continuing Phase 0 design.

## DECISIONS

- BTC only for initial scope.
- Planned forecast horizons: 4h, 24h, 7d.
- No real-money execution in Phase 0-5.
- No live ingestion until source registry and canonical data schemas are committed.
- Forecasts and RAW data are immutable; revisions create new versions/records.
- Complex models must beat simple baselines and the current champion before promotion.

## FILES CHANGED

`README.md`, `START_HERE.md`, `AGENTS.md`, `PROJECT_CONSTITUTION.md`, `PROJECT_STATE.json`, `CHECKPOINT_INDEX.json`, `ROADMAP.md`, `ARCHITECTURE.md`, `docs/architecture/DATA_ARCHITECTURE.md`, `docs/architecture/FORECAST_LEDGER.md`, `docs/architecture/MODEL_LIFECYCLE.md`, `docs/architecture/BTC_MVP.md`, this checkpoint.

## VALIDATION

Verify current `main` is `09f27b...` or a descendant containing only checkpoint/pointer metadata fixes, and verify `PROJECT_STATE.json.current_checkpoint` equals `CHECKPOINT_INDEX.json.latest`.

## SAFETY BOUNDARIES

Research/architecture only. No exchange credentials, no order execution, no portfolio capital, no live trading.

## ONE NEXT ACTION

Define and commit the Phase 0 data-source registry and canonical schemas for RAW, normalized observations, data snapshots, forecasts, and outcomes; keep scope BTC-only and do not start live ingestion yet.
