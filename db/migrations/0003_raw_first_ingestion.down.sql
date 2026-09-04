BEGIN;

DROP FUNCTION IF EXISTS ci_ingest_raw_observation(
  uuid,text,text,timestamptz,timestamptz,timestamptz,timestamptz,timestamptz,
  text,uuid,text,text,text,uuid,text,text,text,numeric,text,timestamptz,timestamptz,
  text,text,text
);

DROP TRIGGER IF EXISTS observation_raw_events_append_only ON observation_raw_events;
DROP TRIGGER IF EXISTS observations_append_only ON observations;
DROP INDEX IF EXISTS raw_events_request_content_uidx;

COMMIT;
