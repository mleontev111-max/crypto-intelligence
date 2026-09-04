BEGIN;

CREATE OR REPLACE FUNCTION ci_forbid_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'append-only table % cannot be %', TG_TABLE_NAME, TG_OP;
END;
$$;

CREATE TABLE data_sources (
  source_id text PRIMARY KEY,
  category text NOT NULL,
  provider text NOT NULL,
  dataset text NOT NULL,
  status text NOT NULL,
  point_in_time_rating text NOT NULL,
  revision_policy text NOT NULL,
  terms_review_status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE raw_events (
  raw_event_id uuid PRIMARY KEY,
  source_id text NOT NULL REFERENCES data_sources(source_id),
  source_record_id text,
  source_event_at timestamptz,
  provider_published_at timestamptz,
  observed_at timestamptz,
  ingested_at timestamptz NOT NULL,
  available_at timestamptz NOT NULL,
  revision_text text,
  supersedes_raw_event_id uuid REFERENCES raw_events(raw_event_id),
  content_hash text NOT NULL,
  payload_ref text NOT NULL,
  mime_type text,
  schema_version text NOT NULL DEFAULT '0.1'
);
CREATE INDEX raw_events_source_available_idx ON raw_events(source_id, available_at);
CREATE INDEX raw_events_source_record_idx ON raw_events(source_id, source_record_id);
CREATE INDEX raw_events_content_hash_idx ON raw_events(content_hash);

CREATE TABLE observations (
  observation_id uuid PRIMARY KEY,
  metric_id text NOT NULL,
  asset text NOT NULL,
  venue text,
  value numeric(38,18) NOT NULL,
  unit text NOT NULL,
  event_at timestamptz NOT NULL,
  available_at timestamptz NOT NULL,
  revision_text text,
  quality_status text NOT NULL CHECK (quality_status IN ('valid','suspect','missing_repaired')),
  normalizer_version text NOT NULL,
  schema_version text NOT NULL DEFAULT '0.1'
);
CREATE INDEX observations_metric_asset_event_idx ON observations(metric_id, asset, event_at);
CREATE INDEX observations_metric_asset_available_idx ON observations(metric_id, asset, available_at);

CREATE TABLE observation_raw_events (
  observation_id uuid NOT NULL REFERENCES observations(observation_id),
  raw_event_id uuid NOT NULL REFERENCES raw_events(raw_event_id),
  PRIMARY KEY (observation_id, raw_event_id)
);

CREATE TABLE data_snapshots (
  data_snapshot_id uuid PRIMARY KEY,
  created_at timestamptz NOT NULL,
  cutoff_available_at timestamptz NOT NULL,
  manifest_hash text NOT NULL UNIQUE,
  notes text,
  schema_version text NOT NULL DEFAULT '0.1'
);

CREATE TABLE data_snapshot_components (
  data_snapshot_id uuid NOT NULL REFERENCES data_snapshots(data_snapshot_id),
  dataset_id text NOT NULL,
  version_or_query_hash text NOT NULL,
  max_available_at timestamptz NOT NULL,
  row_count bigint CHECK (row_count IS NULL OR row_count >= 0),
  PRIMARY KEY (data_snapshot_id, dataset_id)
);

CREATE TABLE model_versions (
  model_version_id text PRIMARY KEY,
  model_family text NOT NULL,
  created_at timestamptz NOT NULL,
  code_commit_sha text NOT NULL,
  training_snapshot_id uuid NOT NULL REFERENCES data_snapshots(data_snapshot_id),
  calibration_snapshot_id uuid REFERENCES data_snapshots(data_snapshot_id),
  config_hash text NOT NULL,
  artifact_ref text NOT NULL,
  calibration_method text,
  status text NOT NULL CHECK (status IN ('baseline','challenger','champion','retired')),
  parent_model_version_id text REFERENCES model_versions(model_version_id),
  schema_version text NOT NULL DEFAULT '0.1'
);

CREATE TABLE target_definitions (
  target_definition_id text PRIMARY KEY,
  asset_scope text NOT NULL,
  horizon text NOT NULL CHECK (horizon IN ('4h','24h','7d')),
  definition_json jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  code_commit_sha text NOT NULL,
  status text NOT NULL,
  notes text
);

CREATE TABLE forecasts (
  forecast_id uuid PRIMARY KEY,
  created_at timestamptz NOT NULL,
  asset text NOT NULL CHECK (asset = 'BTC'),
  horizon text NOT NULL CHECK (horizon IN ('4h','24h','7d')),
  target_definition_id text NOT NULL REFERENCES target_definitions(target_definition_id),
  venue text NOT NULL,
  symbol text NOT NULL,
  reference_price numeric(38,18) NOT NULL CHECK (reference_price > 0),
  reference_observed_at timestamptz NOT NULL,
  model_version_id text NOT NULL REFERENCES model_versions(model_version_id),
  data_snapshot_id uuid NOT NULL REFERENCES data_snapshots(data_snapshot_id),
  market_regime_id text,
  expected_return numeric(24,18),
  confidence_note text,
  status text NOT NULL CHECK (status IN ('open','closed','void')),
  void_reason text,
  schema_version text NOT NULL DEFAULT '0.1'
);
CREATE INDEX forecasts_asset_horizon_created_idx ON forecasts(asset, horizon, created_at);
CREATE INDEX forecasts_model_horizon_created_idx ON forecasts(model_version_id, horizon, created_at);
CREATE INDEX forecasts_status_created_idx ON forecasts(status, created_at);

CREATE TABLE forecast_probabilities (
  forecast_id uuid NOT NULL REFERENCES forecasts(forecast_id),
  class_key text NOT NULL,
  probability numeric(20,18) NOT NULL CHECK (probability >= 0 AND probability <= 1),
  PRIMARY KEY (forecast_id, class_key)
);

CREATE TABLE forecast_outcomes (
  outcome_id uuid PRIMARY KEY,
  forecast_id uuid NOT NULL UNIQUE REFERENCES forecasts(forecast_id),
  resolved_at timestamptz NOT NULL,
  target_definition_id text NOT NULL REFERENCES target_definitions(target_definition_id),
  realized_class text NOT NULL,
  realized_return numeric(24,18) NOT NULL,
  maximum_favorable_excursion numeric(24,18),
  maximum_adverse_excursion numeric(24,18),
  resolution_data_snapshot_id uuid NOT NULL REFERENCES data_snapshots(data_snapshot_id),
  resolution_rule_version text,
  notes text,
  schema_version text NOT NULL DEFAULT '0.1'
);

CREATE TRIGGER raw_events_append_only
BEFORE UPDATE OR DELETE ON raw_events
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE TRIGGER data_snapshots_append_only
BEFORE UPDATE OR DELETE ON data_snapshots
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE TRIGGER model_versions_append_only
BEFORE UPDATE OR DELETE ON model_versions
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE TRIGGER target_definitions_append_only
BEFORE UPDATE OR DELETE ON target_definitions
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE TRIGGER forecasts_append_only
BEFORE UPDATE OR DELETE ON forecasts
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE TRIGGER forecast_probabilities_append_only
BEFORE UPDATE OR DELETE ON forecast_probabilities
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE TRIGGER forecast_outcomes_append_only
BEFORE UPDATE OR DELETE ON forecast_outcomes
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

COMMIT;
