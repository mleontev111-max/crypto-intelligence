#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "START_HERE.md",
    "AGENTS.md",
    "PROJECT_CONSTITUTION.md",
    "PROJECT_STATE.json",
    "CHECKPOINT_INDEX.json",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "docs/architecture/DATA_SOURCE_REGISTRY.md",
    "docs/architecture/CANONICAL_DATA_CONTRACTS.md",
    "schemas/raw-event.schema.json",
    "schemas/observation.schema.json",
    "schemas/data-snapshot.schema.json",
    "schemas/model-version.schema.json",
    "schemas/forecast.schema.json",
    "schemas/outcome.schema.json",
]

JSON_FILES = [
    "PROJECT_STATE.json",
    "CHECKPOINT_INDEX.json",
    "schemas/raw-event.schema.json",
    "schemas/observation.schema.json",
    "schemas/data-snapshot.schema.json",
    "schemas/model-version.schema.json",
    "schemas/forecast.schema.json",
    "schemas/outcome.schema.json",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_json(path: str):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot parse {path}: {exc}")


def require_schema_fields(schema, path, required_fields):
    required = set(schema.get("required", []))
    missing = set(required_fields) - required
    if missing:
        fail(f"{path} missing required contract fields: {sorted(missing)}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing canonical files: {missing}")

    parsed = {path: load_json(path) for path in JSON_FILES}
    state = parsed["PROJECT_STATE.json"]
    index = parsed["CHECKPOINT_INDEX.json"]

    checkpoint = state.get("current_checkpoint")
    if not checkpoint or not isinstance(checkpoint, str):
        fail("PROJECT_STATE.current_checkpoint must be a non-empty string")
    if checkpoint != index.get("latest"):
        fail("PROJECT_STATE.current_checkpoint != CHECKPOINT_INDEX.latest")
    if not (ROOT / checkpoint).is_file():
        fail(f"current checkpoint does not exist: {checkpoint}")

    next_action = state.get("one_next_action")
    if not isinstance(next_action, str) or not next_action.strip():
        fail("active project must have a non-empty one_next_action")

    if state.get("status") == "active" and state.get("phase") != "0":
        fail("Phase 0 guard expected PROJECT_STATE.phase == '0'")
    if state.get("live_trading_allowed") is not False:
        fail("live_trading_allowed must remain false in Phase 0")
    if state.get("live_ingestion_allowed", False) is not False:
        fail("live_ingestion_allowed must remain false until explicitly gated later")

    require_schema_fields(parsed["schemas/raw-event.schema.json"], "raw-event", [
        "raw_event_id", "source_id", "ingested_at", "available_at", "content_hash", "payload_ref"
    ])
    require_schema_fields(parsed["schemas/observation.schema.json"], "observation", [
        "observation_id", "metric_id", "event_at", "available_at", "raw_event_ids"
    ])
    require_schema_fields(parsed["schemas/data-snapshot.schema.json"], "data-snapshot", [
        "data_snapshot_id", "cutoff_available_at", "manifest_hash", "components"
    ])
    require_schema_fields(parsed["schemas/model-version.schema.json"], "model-version", [
        "model_version_id", "code_commit_sha", "training_snapshot_id", "config_hash", "artifact_ref", "status"
    ])
    require_schema_fields(parsed["schemas/forecast.schema.json"], "forecast", [
        "forecast_id", "created_at", "horizon", "target_definition_id", "model_version_id", "data_snapshot_id", "probabilities"
    ])
    require_schema_fields(parsed["schemas/outcome.schema.json"], "outcome", [
        "outcome_id", "forecast_id", "target_definition_id", "realized_class", "resolution_data_snapshot_id"
    ])

    forecast = parsed["schemas/forecast.schema.json"]
    horizons = forecast.get("properties", {}).get("horizon", {}).get("enum")
    if horizons != ["4h", "24h", "7d"]:
        fail(f"forecast horizon enum drifted: {horizons}")

    print("PASS: Phase 0 canonical contracts/state are internally consistent")


if __name__ == "__main__":
    main()
