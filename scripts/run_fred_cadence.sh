#!/bin/bash
# Stage 1 cadence wrapper: one bounded, FRED-only collection run.
#
# NOT installed as a scheduled job by this commit. This script is meant to
# be invoked by a launchd job that does not exist yet
# (see docs/operations/launchd/com.crypto-intelligence.fred-cadence.plist.template
# and docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md, Stage 1). Running
# it by hand is equivalent to any other manual bounded collection.
#
# It computes an explicit bounded window (today, minus a 10-calendar-day
# observation lookback) and invokes the existing collector with
# --sources fred only — it never touches Coinbase. All windowing/PIT and
# idempotency guarantees are the same as any other manual collector run;
# this script adds no new ingestion logic.
set -euo pipefail

# launchd jobs get a minimal PATH; make sure docker is found regardless of
# who/what invokes this script.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if [ ! -f .env ]; then
  echo "FRED cadence: .env not found at ${REPO_ROOT}/.env — refusing to run" >&2
  exit 1
fi

REALTIME_DATE="$(date -u +%Y-%m-%d)"
OBSERVATION_END="${REALTIME_DATE}"
OBSERVATION_START="$(date -u -v-10d +%Y-%m-%d)"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FRED cadence: realtime_date=${REALTIME_DATE} observation_start=${OBSERVATION_START} observation_end=${OBSERVATION_END}"

docker compose --profile manual run --rm collector \
  --write \
  --sources fred \
  --fred-realtime-date "${REALTIME_DATE}" \
  --fred-observation-start "${OBSERVATION_START}" \
  --fred-observation-end "${OBSERVATION_END}"
