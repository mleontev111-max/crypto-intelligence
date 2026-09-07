# Phase 0 Checkpoint — FRED Cadence Stage 1 Prepared (Not Loaded)

Date: 2026-09-07
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Execute Stage 1 preparation from `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`
(FRED-only cadence): re-verify the FRED publish time, give the collector a
genuine single-source mode, write the wrapper script and a `launchd`
template, and verify all of it live — **without** loading the job or
touching `PROJECT_STATE.live_ingestion_allowed`, per the plan's own gate
that loading requires a separate explicit owner approval and checkpoint.

## SUMMARIZED STATE SHA

`626811a49f8c64fa183840a41d165971fd6684fe`

This is the exact implementation state summarized by this checkpoint.

## WHAT CHANGED

- **`scripts/collect_approved_sources.py`:** added `--sources
  {all,coinbase,fred}` (default `all`). Only the flags for the selected
  source(s) are now required; the DB-write bundle and JSON summary include
  only the source(s) actually collected. Default behavior (`--sources`
  omitted) is unchanged byte-for-byte in shape — confirmed by the existing
  CI-covered scenario still passing locally (see VERIFIED).
- **`tests/test_collector_source_selection.py`** (new): three tests
  confirming `--sources fred` does not require Coinbase args, `--sources
  coinbase` does not require the FRED key/window, and default (`all`)
  still requires everything.
- **`scripts/run_fred_cadence.sh`** (new, executable): computes
  `realtime_date = today (UTC)`, `observation_start = today − 10 days`,
  `observation_end = today`, and invokes
  `docker compose --profile manual run --rm collector --write --sources
  fred ...` with those values. Not registered with any scheduler.
- **`docs/operations/launchd/com.crypto-intelligence.fred-cadence.plist.template`**
  (new): a `launchd` `LaunchAgent` template (user agent, not a root
  daemon, because Docker Desktop runs in the user session) with
  `StartCalendarInterval` `Hour=1, Minute=0` in this host's local time
  zone. Explicitly a `.template` file — not copied into
  `~/Library/LaunchAgents/`, not loaded.
- **`docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`:** corrected the
  FRED run time from the earlier unconfirmed `14:00 UTC` guess to
  confirmed `22:00 UTC` (with citation), and updated the Stage 1 checklist
  to mark steps 1–3 done and steps 4–5 (load the job / run gap-checks) as
  still outstanding.
- **`docs/operations/SINGLE_NODE_RUNTIME_v0.1.md`:** documented the new
  `--sources` flag.
- **`.gitignore`:** added `logs/` (the `launchd` template writes there;
  directory does not exist yet and nothing has been logged).

## VERIFIED

- FRED publish time: fetched `https://www.federalreserve.gov/releases/h15/`
  directly — "The release is posted daily Monday through Friday at
  4:15pm" (Board of Governors, Washington DC, Eastern Time). `22:00 UTC`
  is safely after that in both EDT (18:00 ET) and EST (17:00 ET).
- `python3 -m unittest discover -s tests`: **44/44 tests pass**, including
  the 3 new source-selection tests and all previously existing tests
  (adapters, disabled-default, raw-first ingestion, read-only transport).
- `docker compose build collector`: rebuilt successfully with the new
  code.
- Disabled-by-default check still returns exactly
  `{"database_write_performed": false, "network_fetch_performed": false,
  "status": "disabled", ...}` — unchanged by the `--sources` addition.
- Live bounded `--sources fred` run reusing the already-collected
  2026-09-01 window: summary contained only `fred_dgs2`/`fred_dgs10` keys
  (no `coinbase` key), same `payload_ref`/`sha256` as the original
  collection (idempotent), and DB counts stayed at 3 `raw_events` / 30
  `observations` / 30 `observation_raw_events` — confirms no duplicate
  writes and no accidental Coinbase fetch.
- Live run of `scripts/run_fred_cadence.sh` itself, with a genuinely fresh
  window (`realtime_date=2026-09-07`, `observation_start=2026-08-28`,
  `observation_end=2026-09-07`): succeeded, `http_status=200` for both
  series, 5 observations each. DB counts after: 5 `raw_events` (3 original
  + 2 new), 40 `observations` (30 + 10 new), 40 `observation_raw_events` —
  matches expectations exactly, and 5 `.bin` files confirmed on disk via
  the `raw_data` volume.
- `plutil -lint docs/operations/launchd/com.crypto-intelligence.fred-cadence.plist.template`:
  `OK`.
- Host time zone: `date +%Z%z` → `MSK +0300`;
  `readlink /etc/localtime` → `.../Europe/Moscow` — confirms the plist's
  local `01:00` Hour is a stable, correct mapping to `22:00 UTC`
  year-round (fixed offset, no DST).
- `docker compose ps` before and after this session's work: only
  `crypto-intelligence-db-1` running throughout; no scheduler or
  additional container appeared.
- `git fetch origin` + `git rev-parse main origin/main` matched before
  this session's edits (`626811a...`), confirming no drift at start.

## UNKNOWN

- How long "a stable unattended period" for Stage 1 should run before
  Stage 2 (Coinbase) begins is still not numerically defined — left to the
  owner's judgment, as in the prior checkpoint.
- The gap-check report (expected-vs-actual buckets/dates) described in the
  cadence proposal is still only a sketch; not built this session.

## BLOCKERS

None for the preparation work itself. The remaining blocker to actually
running Stage 1 unattended is the explicit owner decision described in
SAFETY BOUNDARIES / ONE NEXT ACTION below — by design, not an accident.

## DECISIONS

- Added a minimal `--sources` selector to the collector rather than
  redefining "Stage 1 = FRED-only" to mean "the full collector still runs
  but only FRED is scheduled" — this was an explicit owner choice this
  session over the alternative of leaving the collector as always-both and
  accepting a daily incidental Coinbase write as a side effect.
- The `launchd` plist is deliberately shipped as a `.template` (not a
  loadable `.plist` at a real `LaunchAgents` path) so nothing in this
  repository can accidentally self-install a recurring job.
- Two real (not fixture) bounded collections were run this session
  (`--sources fred` on the known window, and a fresh-window run via the
  wrapper) to prove the new code path end-to-end against the live FRED
  API before committing it — consistent with this project's practice of
  live-verifying collector behavior rather than trusting fixtures alone.
  Both were manual, explicitly invoked, bounded runs — not scheduling.

## FILES CHANGED

- `scripts/collect_approved_sources.py` (modified: `--sources` flag).
- `tests/test_collector_source_selection.py` (new).
- `scripts/run_fred_cadence.sh` (new, executable).
- `docs/operations/launchd/com.crypto-intelligence.fred-cadence.plist.template` (new).
- `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md` (updated).
- `docs/operations/SINGLE_NODE_RUNTIME_v0.1.md` (updated).
- `.gitignore` (added `logs/`).
- This checkpoint file.
- `CHECKPOINT_INDEX.json` and `PROJECT_STATE.json` pointers (see below).

## VALIDATION

- `python3 -m unittest discover -s tests`: 44/44 pass.
- `docker compose config --quiet`: valid.
- `docker compose build collector`: succeeds.
- Two live bounded collections against the real Coinbase/FRED APIs on this
  host, detailed in VERIFIED, with exact before/after row counts checked
  via `psql`.
- `plutil -lint` on the new plist template.

## SAFETY BOUNDARIES

- `PROJECT_STATE.live_ingestion_allowed` **unchanged, still `false`**.
- **No `launchd` job was loaded.** The plist exists only as a `.template`
  file inside the repo; it was never copied to `~/Library/LaunchAgents/`
  and `launchctl load` was never run.
- `docker compose ps` shows only `db` running after this session; no
  scheduler, cron entry, or background process exists.
- Both live collections performed this session were manual, explicit,
  bounded invocations — not automation, and not a repeated/regular
  cadence in the sense the project treats as requiring
  `live_ingestion_allowed=true`.
- No trading/execution.
- Only the already-approved Coinbase BTC-USD candles and FRED DGS2/DGS10
  were touched; the `--sources` flag does not add any new source.
- FRED key remained host-`.env`-only; both collector summaries printed
  this session redact it (`api_key=REDACTED`), verified directly in the
  printed output.

## ONE NEXT ACTION

Stage 1 is technically ready but **not enabled**. The next action is an
explicit owner decision, not further engineering: approve copying
`docs/operations/launchd/com.crypto-intelligence.fred-cadence.plist.template`
to `~/Library/LaunchAgents/com.crypto-intelligence.fred-cadence.plist`,
running `mkdir -p logs` and `launchctl load` on it, and flipping
`PROJECT_STATE.live_ingestion_allowed` for this one FRED-only cadence —
all three together, recorded in their own checkpoint immediately after.
Do not begin Stage 2 (Coinbase) until Stage 1 has then run unattended long
enough for the owner to be comfortable, per
`docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`.
