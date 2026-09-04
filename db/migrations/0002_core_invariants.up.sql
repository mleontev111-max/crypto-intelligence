BEGIN;

CREATE OR REPLACE FUNCTION ci_validate_snapshot_component_cutoff()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  parent_cutoff timestamptz;
BEGIN
  SELECT cutoff_available_at
    INTO parent_cutoff
    FROM data_snapshots
   WHERE data_snapshot_id = NEW.data_snapshot_id;

  IF parent_cutoff IS NULL THEN
    RAISE EXCEPTION 'data snapshot % not found', NEW.data_snapshot_id;
  END IF;

  IF NEW.max_available_at > parent_cutoff THEN
    RAISE EXCEPTION 'snapshot component max_available_at % exceeds cutoff %', NEW.max_available_at, parent_cutoff;
  END IF;

  RETURN NEW;
END;
$$;

CREATE TRIGGER data_snapshot_components_cutoff_guard
BEFORE INSERT OR UPDATE ON data_snapshot_components
FOR EACH ROW EXECUTE FUNCTION ci_validate_snapshot_component_cutoff();

CREATE OR REPLACE FUNCTION ci_validate_forecast_probability_vector()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  probability_sum numeric;
  probability_count integer;
BEGIN
  SELECT sum(probability), count(*)
    INTO probability_sum, probability_count
    FROM forecast_probabilities
   WHERE forecast_id = NEW.forecast_id;

  IF probability_count < 2 THEN
    RAISE EXCEPTION 'forecast % must have at least two probability classes', NEW.forecast_id;
  END IF;

  IF abs(probability_sum - 1.0) > 0.000000000001 THEN
    RAISE EXCEPTION 'forecast % probability sum % is outside tolerance', NEW.forecast_id, probability_sum;
  END IF;

  RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER forecast_probability_vector_guard
AFTER INSERT ON forecast_probabilities
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION ci_validate_forecast_probability_vector();

CREATE OR REPLACE FUNCTION ci_validate_outcome_target_definition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  forecast_target text;
BEGIN
  SELECT target_definition_id
    INTO forecast_target
    FROM forecasts
   WHERE forecast_id = NEW.forecast_id;

  IF forecast_target IS NULL THEN
    RAISE EXCEPTION 'forecast % not found', NEW.forecast_id;
  END IF;

  IF NEW.target_definition_id <> forecast_target THEN
    RAISE EXCEPTION 'outcome target_definition_id % does not match forecast target_definition_id %', NEW.target_definition_id, forecast_target;
  END IF;

  RETURN NEW;
END;
$$;

CREATE TRIGGER forecast_outcome_target_guard
BEFORE INSERT ON forecast_outcomes
FOR EACH ROW EXECUTE FUNCTION ci_validate_outcome_target_definition();

COMMIT;
