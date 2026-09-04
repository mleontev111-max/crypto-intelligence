BEGIN;

DROP TABLE IF EXISTS forecast_outcomes;
DROP TABLE IF EXISTS forecast_probabilities;
DROP TABLE IF EXISTS forecasts;
DROP TABLE IF EXISTS target_definitions;
DROP TABLE IF EXISTS model_versions;
DROP TABLE IF EXISTS data_snapshot_components;
DROP TABLE IF EXISTS data_snapshots;
DROP TABLE IF EXISTS observation_raw_events;
DROP TABLE IF EXISTS observations;
DROP TABLE IF EXISTS raw_events;
DROP TABLE IF EXISTS data_sources;
DROP FUNCTION IF EXISTS ci_forbid_mutation();

COMMIT;
