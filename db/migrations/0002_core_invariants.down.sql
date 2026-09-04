BEGIN;

DROP TRIGGER IF EXISTS forecast_outcome_target_guard ON forecast_outcomes;
DROP FUNCTION IF EXISTS ci_validate_outcome_target_definition();

DROP TRIGGER IF EXISTS forecast_probability_vector_guard ON forecast_probabilities;
DROP FUNCTION IF EXISTS ci_validate_forecast_probability_vector();

DROP TRIGGER IF EXISTS data_snapshot_components_cutoff_guard ON data_snapshot_components;
DROP FUNCTION IF EXISTS ci_validate_snapshot_component_cutoff();

COMMIT;
