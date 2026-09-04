# PostgreSQL Mapping v0.1

Status: Phase 0 design. This is a logical-to-physical mapping specification, not a migration and not approval for live ingestion.

## Database principles

- PostgreSQL is the canonical operational store.
- TimescaleDB may be added for high-volume time-series tables after volume/query requirements are measured.
- UTC timestamps only in canonical columns.
- RAW evidence is immutable.
- Provider revisions append new rows; historical point-in-time state is not rewritten.
- Foreign keys preserve provenance from forecast back to data/model state.

## Proposed tables

### `data_sources`
Registry mirror for approved/candidate feeds.

Primary key: `source_id text`.
Key fields: category, provider, dataset, status, point_in_time_rating, revision_policy, terms_review_status, created_at, updated_at.

### `raw_events`
Physical mapping of `raw-event.schema.json`.

Primary key: `raw_event_id uuid`.
Important columns: source_id, source_record_id, source_event_at, provider_published_at, observed_at, ingested_at, available_at, revision_text, supersedes_raw_event_id, content_hash, payload_ref, mime_type, schema_version.

Constraints/indexes:
- FK source_id -> data_sources.
- optional self-FK supersedes_raw_event_id.
- unique `(source_id, content_hash)` only if provider semantics make this safe; otherwise index, not uniqueness.
- indexes on `(source_id, available_at)`, `(source_id, source_record_id)`, `content_hash`.
- no UPDATE of evidence fields after insert except separately audited administrative metadata if ever required.

### `observations`
Normalized numeric facts.

Primary key: `observation_id uuid`.
Columns: metric_id, asset, venue, value numeric, unit, event_at, available_at, revision_text, quality_status, normalizer_version, schema_version.

Indexes: `(metric_id, asset, event_at)`, `(metric_id, asset, available_at)`.

Potential future Timescale hypertable candidate: yes, after benchmark.

### `observation_raw_events`
Many-to-many provenance join.

Primary key: `(observation_id, raw_event_id)`.
FKs to observations/raw_events.

### `data_snapshots`
Manifest identity for a point-in-time model decision.

Primary key: `data_snapshot_id uuid`.
Columns: created_at, cutoff_available_at, manifest_hash, notes, schema_version.
Unique index on manifest_hash if canonical serialization guarantees deterministic identity.

### `data_snapshot_components`
Rows describing each dataset/version/query included in a snapshot.

Primary key: `(data_snapshot_id, dataset_id)`.
Columns: version_or_query_hash, max_available_at, row_count.
Constraint: `max_available_at <= parent.cutoff_available_at` must be enforced by application/trigger because a simple CHECK cannot reference parent row.

### `model_versions`
Immutable model artifact registry.

Primary key: `model_version_id text`.
Columns: model_family, created_at, code_commit_sha, training_snapshot_id, calibration_snapshot_id, config_hash, artifact_ref, calibration_method, status, parent_model_version_id, schema_version.
FKs training/calibration snapshot -> data_snapshots.

Model status history should eventually move to a separate append-only transition table so promotion does not mutate scientific evidence.

### `target_definitions`
Versioned forecast target semantics.

Primary key: `target_definition_id text`.
Columns: asset_scope, horizon, definition_json jsonb, created_at, code_commit_sha, status, notes.

This table is intentionally separate because DOWN/RANGE/UP thresholds are still under research.

### `forecasts`
Immutable forecast header.

Primary key: `forecast_id uuid`.
Columns: created_at, asset, horizon, target_definition_id, venue, symbol, reference_price, reference_observed_at, model_version_id, data_snapshot_id, market_regime_id, expected_return, confidence_note, status, void_reason, schema_version.

FKs target_definition_id, model_version_id, data_snapshot_id.
Indexes: `(asset, horizon, created_at)`, `(model_version_id, horizon, created_at)`, `(status, created_at)`.

### `forecast_probabilities`
Normalized class probability vector.

Primary key: `(forecast_id, class_key)`.
Columns: probability numeric.
CHECK probability between 0 and 1.
Application/database deferred constraint must enforce probabilities sum to 1 within defined tolerance before forecast publication.

### `forecast_outcomes`
Append-only resolution record.

Primary key: `outcome_id uuid`.
Unique FK: `forecast_id` -> forecasts to ensure one canonical resolution per forecast version unless a later versioning rule explicitly changes this.
Columns: resolved_at, target_definition_id, realized_class, realized_return, MFE, MAE, resolution_data_snapshot_id, resolution_rule_version, notes, schema_version.

Constraint/invariant: outcome target_definition_id must equal forecast target_definition_id.

### Future tables not yet approved

- market regimes / regime transitions
- features / feature definitions
- model evaluations
- champion/challenger promotion history
- paper portfolio / simulated orders
- news events / entity links
- wallet entities / attribution evidence

They remain outside the first physical schema until their contracts are defined.

## Transaction boundaries

A published forecast should be created atomically with:

1. existing immutable data_snapshot;
2. existing immutable model_version;
3. existing target_definition;
4. forecast row;
5. full probability vector.

If any invariant fails, no forecast is published.

Outcome resolution is a separate later transaction and never rewrites the original forecast.

## Phase 0 migration gate

Before writing SQL migrations:

- contract guard must pass on exact main;
- target-definition research may remain OPEN, but table must support versioning;
- choose UUID generation strategy;
- decide whether TimescaleDB is required immediately or deferred;
- define append-only enforcement strategy for RAW and Forecast records;
- define numeric precision for prices, returns and probabilities.

No live ingestion begins merely because migrations exist.