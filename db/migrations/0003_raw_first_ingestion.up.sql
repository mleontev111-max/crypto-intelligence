BEGIN;

-- Exact repeats of the same logical provider request + identical bytes are one RAW fact.
-- The same source_record_id with different content_hash is a revision and remains append-only.
CREATE UNIQUE INDEX raw_events_request_content_uidx
ON raw_events(source_id, source_record_id, content_hash)
WHERE source_record_id IS NOT NULL;

CREATE TRIGGER observations_append_only
BEFORE UPDATE OR DELETE ON observations
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE TRIGGER observation_raw_events_append_only
BEFORE UPDATE OR DELETE ON observation_raw_events
FOR EACH ROW EXECUTE FUNCTION ci_forbid_mutation();

CREATE OR REPLACE FUNCTION ci_ingest_raw_observation(
  p_raw_event_id uuid,
  p_source_id text,
  p_source_record_id text,
  p_source_event_at timestamptz,
  p_provider_published_at timestamptz,
  p_observed_at timestamptz,
  p_ingested_at timestamptz,
  p_available_at timestamptz,
  p_revision_text text,
  p_supersedes_raw_event_id uuid,
  p_content_hash text,
  p_payload_ref text,
  p_mime_type text,
  p_observation_id uuid,
  p_metric_id text,
  p_asset text,
  p_venue text,
  p_value numeric,
  p_unit text,
  p_event_at timestamptz,
  p_observation_available_at timestamptz,
  p_observation_revision_text text,
  p_quality_status text,
  p_normalizer_version text
)
RETURNS TABLE(raw_event_id uuid, observation_id uuid, raw_inserted boolean, observation_inserted boolean)
LANGUAGE plpgsql
AS $$
DECLARE
  v_raw_event_id uuid;
  v_observation_id uuid;
  v_raw_inserted boolean := false;
  v_observation_inserted boolean := false;
BEGIN
  IF p_source_record_id IS NULL OR btrim(p_source_record_id) = '' THEN
    RAISE EXCEPTION 'source_record_id is required for idempotent ingestion';
  END IF;
  IF p_content_hash IS NULL OR btrim(p_content_hash) = '' THEN
    RAISE EXCEPTION 'content_hash is required';
  END IF;
  IF p_available_at > p_ingested_at THEN
    RAISE EXCEPTION 'raw available_at cannot be after ingested_at';
  END IF;
  IF p_observation_available_at < p_available_at THEN
    RAISE EXCEPTION 'observation available_at cannot predate RAW available_at';
  END IF;
  IF p_event_at IS NULL THEN
    RAISE EXCEPTION 'observation event_at is required';
  END IF;

  INSERT INTO raw_events(
    raw_event_id, source_id, source_record_id, source_event_at,
    provider_published_at, observed_at, ingested_at, available_at,
    revision_text, supersedes_raw_event_id, content_hash, payload_ref, mime_type
  ) VALUES (
    p_raw_event_id, p_source_id, p_source_record_id, p_source_event_at,
    p_provider_published_at, p_observed_at, p_ingested_at, p_available_at,
    p_revision_text, p_supersedes_raw_event_id, p_content_hash, p_payload_ref, p_mime_type
  )
  ON CONFLICT (source_id, source_record_id, content_hash) WHERE source_record_id IS NOT NULL
  DO NOTHING
  RETURNING raw_events.raw_event_id INTO v_raw_event_id;

  IF v_raw_event_id IS NOT NULL THEN
    v_raw_inserted := true;
  ELSE
    SELECT r.raw_event_id INTO v_raw_event_id
    FROM raw_events r
    WHERE r.source_id = p_source_id
      AND r.source_record_id = p_source_record_id
      AND r.content_hash = p_content_hash;
  END IF;

  INSERT INTO observations(
    observation_id, metric_id, asset, venue, value, unit,
    event_at, available_at, revision_text, quality_status, normalizer_version
  ) VALUES (
    p_observation_id, p_metric_id, p_asset, p_venue, p_value, p_unit,
    p_event_at, p_observation_available_at, p_observation_revision_text,
    p_quality_status, p_normalizer_version
  )
  ON CONFLICT (observation_id) DO NOTHING
  RETURNING observations.observation_id INTO v_observation_id;

  IF v_observation_id IS NOT NULL THEN
    v_observation_inserted := true;
  ELSE
    SELECT o.observation_id INTO v_observation_id
    FROM observations o
    WHERE o.observation_id = p_observation_id;

    IF NOT EXISTS (
      SELECT 1
      FROM observations o
      WHERE o.observation_id = p_observation_id
        AND o.metric_id = p_metric_id
        AND o.asset = p_asset
        AND o.venue IS NOT DISTINCT FROM p_venue
        AND o.value = p_value
        AND o.unit = p_unit
        AND o.event_at = p_event_at
        AND o.available_at = p_observation_available_at
        AND o.revision_text IS NOT DISTINCT FROM p_observation_revision_text
        AND o.quality_status = p_quality_status
        AND o.normalizer_version = p_normalizer_version
    ) THEN
      RAISE EXCEPTION 'observation_id collision with different immutable content';
    END IF;
  END IF;

  INSERT INTO observation_raw_events(observation_id, raw_event_id)
  VALUES (v_observation_id, v_raw_event_id)
  ON CONFLICT DO NOTHING;

  RETURN QUERY SELECT v_raw_event_id, v_observation_id, v_raw_inserted, v_observation_inserted;
END;
$$;

COMMIT;
