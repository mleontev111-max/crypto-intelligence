# Canonical Data Contracts v0.1

## Purpose

This document links the Phase 0 JSON schemas into one point-in-time chain. Schemas define logical contracts, not yet PostgreSQL tables.

## Chain

`RawEvent -> Observation -> DataSnapshot -> ModelVersion -> Forecast -> Outcome`

### RawEvent
Immutable evidence from an external source. A provider correction creates another record/revision; it never rewrites the historical record that a past forecast could have seen.

### Observation
Normalized fact derived from one or more raw events. It preserves `available_at` and raw provenance.

### DataSnapshot
A manifest of the exact datasets/versions and maximum `available_at` included in a model decision. It does not duplicate all source data.

### ModelVersion
Immutable identity for a trained model artifact, including code commit, training snapshot, configuration hash and optional calibration snapshot/method.

### Forecast
Immutable published probability vector tied to a model version and data snapshot. `target_definition_id` is versioned because DOWN/RANGE/UP semantics are still under research and may change between future models without changing history.

### Outcome
Append-only resolution of a forecast under the same versioned target definition. Outcomes do not mutate the original forecast.

## Timestamp semantics

All canonical timestamps are UTC.

- `source_event_at`: when the source says the underlying event occurred.
- `provider_published_at`: when provider/source published the record, if available.
- `observed_at`: when our collector observed it, if distinct from ingestion.
- `ingested_at`: when our system stored the raw record.
- `available_at`: earliest defensible time the forecasting system could have used the information.

For point-in-time queries, `available_at` is the controlling timestamp. A later provider revision must never make revised history appear available to an earlier forecast.

## Invariants to enforce in application/database validation

JSON Schema cannot express every cross-record rule. Later validation must enforce:

1. `available_at <= forecast.created_at` for every input used by a forecast.
2. every DataSnapshot component has `max_available_at <= cutoff_available_at`.
3. forecast probabilities sum to 1 within a defined numeric tolerance.
4. an Outcome references an existing immutable Forecast.
5. Outcome and Forecast use the same `target_definition_id`.
6. a champion model version cannot be overwritten; promotion creates a state transition/history record.
7. RAW payload/content hashes are immutable.
8. no forecast or outcome is silently deleted to improve historical metrics.

## Explicitly unresolved

- exact BTC target definitions for 4h/24h/7d;
- exact database types/indexes/Timescale hypertables;
- provider-specific revision semantics until source approval;
- evaluation/calibration protocol pending quant research review.

These are UNKNOWN, not implicit defaults.