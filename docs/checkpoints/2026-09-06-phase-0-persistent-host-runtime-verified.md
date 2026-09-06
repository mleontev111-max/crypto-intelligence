# Phase 0 Checkpoint — Persistent-Host Runtime Verified

Date: 2026-09-06
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Deploy the validated `compose.yml` package on the selected persistent host (this Mac mini) and verify that PostgreSQL rows and RAW files from one bounded manual Coinbase/FRED collection survive a database container restart, closing the last Gate A blocker recorded in the prior checkpoint.

## SUMMARIZED STATE SHA

`418a52a30ec12b37d04d933ff9f64fb42fdac6bb`

This is the exact implementation state summarized by this checkpoint. Checkpoint/pointer-only commits may be descendants.

## HOST DETAILS

- Host: `Mac-mini-Mihail.local` (macOS 26.6.2, build 25G83, arm64), used as the selected persistent host.
- Docker version 29.7.2 (build a7dcaa6); Docker Compose v5.4.0.
- `.env` created locally on this host from `.env.example` (not committed; `git check-ignore -v .env` confirms it is ignored by the newly added `.gitignore`). `POSTGRES_PASSWORD` generated locally with `openssl rand -hex 24`; `FRED_API_KEY` provided by the project owner and written only into `.env` on disk (never committed, never printed by the collector — verified redacted in its own summary output).

## WHAT CHANGED

- Added `.gitignore` (the repository previously had none) to keep `.env` and Python/OS cache artifacts out of version control before any secret was written to disk.
- Created host-local `.env` with `POSTGRES_DB`, `POSTGRES_USER`, a freshly generated `POSTGRES_PASSWORD`, and the owner-supplied `FRED_API_KEY`; file permissions restricted to `600`.
- Deployed the `compose.yml` package on this host: started `db` only (no scheduler), applied Phase 0 migrations via `--profile manual run migrate`, verified the collector's default-disabled behavior, ran exactly one bounded manual collection, restarted the `db` container, and re-verified persistence.
- No application/source code changed in this session (the Binance funding/OI adapter commit `418a52a` predates this session and is unrelated candidate work — see NOTE below).

## NOTE ON REQUESTED PRIOR CHECKPOINT

The session was asked to read `docs/checkpoints/2026-09-06-phase-0-binance-funding-oi-candidate-recorded.md`. At the start of this session that file appeared not to exist locally, because this working copy had not been `git fetch`ed and was stale relative to `origin/main` — the file had already been pushed by a separate session (commit `16e6177`) before this session began. This session incorrectly reported the file as nonexistent to the user before discovering the staleness at push time (`git push` was rejected as non-fast-forward). After fetching, that checkpoint was confirmed to exist and to record commit `418a52a` (Binance USD-M Futures funding/OI candidate adapter, status: candidate, not approved) with `one_next_action` carried forward unchanged — identical in substance to the 2026-09-04 checkpoint's action and to this session's task. This checkpoint was then rebased onto the real `origin/main` tip and supersedes `2026-09-06-phase-0-binance-funding-oi-candidate-recorded.md` (now marked `superseded` in `CHECKPOINT_INDEX.json`), which itself superseded `2026-09-04-phase-0-single-node-runtime-verified.md`. Commit `418a52a` remains unrelated candidate source work and does not affect the runtime deployed here.

## VERIFIED

Commands run directly on the persistent host, in order:

1. `docker compose up -d db` — started only `crypto-intelligence-db-1`; became `healthy` on first health-check attempt. No `migrate` or `collector` container started (both remain under the `manual` profile).
2. `docker compose --profile manual run --rm migrate` — both migration transactions (`0001_core_provenance`, `0002_core_invariants`) applied with `BEGIN…COMMIT`, no errors.
3. `docker compose --profile manual run --rm collector` (no args) — returned `{"database_write_performed": false, "network_fetch_performed": false, "status": "disabled", "hint": "pass --write with explicit bounded windows to run the collector"}`. Confirms collector is disabled by default: PASS.
4. `docker compose --profile manual run --rm collector --write --coinbase-start 2026-09-01T00:00:00Z --coinbase-end 2026-09-01T03:00:00Z --fred-realtime-date 2026-09-01 --fred-observation-start 2026-08-25 --fred-observation-end 2026-09-01` (same bounded window already verified in the `Single-Node Runtime Guard` CI job) — returned `status=success`, `http_status=200` for all three source calls, `coinbase.observations=20`, `fred_dgs10.observations=5`, `fred_dgs2.observations=5` (30 total), three distinct `payload_ref` values, and `api_key=REDACTED` in every `safe_url` — the FRED key never appeared in the printed summary.
5. Row counts before restart: `select count(*) from raw_events` = 3; `select count(*) from observations` = 30; `select count(*) from observation_raw_events` = 30.
6. RAW volume before restart: `find /data/raw -type f -name '*.bin'` (via a disposable Alpine container mounting `crypto-intelligence_raw_data`) = 3 files, hashes matching the three `payload_ref` values from step 4.
7. `docker compose restart db` — container returned to `healthy` after 3 health-check polls (~6s).
8. Row counts after restart: `raw_events` = 3; `observations` = 30; `observation_raw_events` = 30 — unchanged.
9. `payload_ref` values after restart match step 4/6 exactly (`file:///data/raw/24/245afda8…bin`, `.../7d/7dadbe88…bin`, `.../82/827e73b1…bin`).
10. RAW volume after restart: 3 `.bin` files present — unchanged.
11. `docker compose ps` / `docker ps -a --filter name=crypto-intelligence` after restart: only `crypto-intelligence-db-1` running; no lingering `migrate`/`collector` containers (both were run with `--rm`); no scheduler service exists in `compose.yml`.
12. `PROJECT_STATE.live_ingestion_allowed` was not modified during this session; remains `false`.

Result: full match against the target evidence bar (3 RAW rows, 30 observations, 30 lineage rows, 3 RAW `.bin` files, all surviving a `db` container restart).

## UNKNOWN

- Long-running host stability (disk pressure, unattended reboot behavior, backup strategy) has not been exercised — only one explicit `docker compose restart db` was tested, not a full host reboot or `docker compose down && up`.
- No regular collection cadence/scheduler has been designed or enabled.
- Whether this Mac mini is the final, permanently dedicated host (power/network reliability over weeks) is an operational decision outside this session's scope.

## BLOCKERS

None. The Gate A blocker recorded in the prior checkpoint (one controlled persistent-host collection with verified restart-survival) is now closed.

## DECISIONS

- This Mac mini (`Mac-mini-Mihail.local`) is confirmed as the running persistent host for the Phase 0 single-node runtime.
- Repository now ships a `.gitignore`; `.env` and common Python/OS artifacts are excluded from version control going forward.
- Scheduling remains explicitly out of scope; only manual, bounded, explicitly-invoked collections are permitted.
- `live_ingestion_allowed` stays `false` — this checkpoint records host evidence only and does not itself authorize regular/scheduled ingestion, which remains a distinct future decision.

## FILES CHANGED

- Added `.gitignore`.
- Added this checkpoint file.
- Updated `CHECKPOINT_INDEX.json` and `PROJECT_STATE.json` (see below).
- No source/schema/migration files changed.
- `.env` was created on the host filesystem only; it is not part of this commit (git-ignored).

## VALIDATION

All validation was manual command execution against the real Docker Compose stack on this host, as enumerated in VERIFIED above. No CI run was invoked in this session; the bounded collection window intentionally reused the exact parameters already validated by the `Single-Node Runtime Guard` CI workflow (`.github/workflows/single-node-runtime-guard.yml`) so host results are directly comparable to that CI evidence.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false` remains unchanged — no regular/scheduled collection is authorized.
- Only one bounded manual collection was performed, matching the prior checkpoint's exact authorization scope; this checkpoint does not itself authorize further collections beyond what a future checkpoint approves.
- No scheduler, cron, or background collector process was started or configured.
- Only approved Coinbase BTC-USD candles and FRED DGS2/DGS10 were fetched; no other sources were touched.
- FRED key remained host-`.env`-only; it was never committed, and the collector's own summary output redacts it (`api_key=REDACTED`), verified in step 4 above.
- No trading/execution of any kind occurred.

## ONE NEXT ACTION

Decide and document a regular (but still explicitly bounded and reviewed) collection cadence proposal for Coinbase/FRED on this persistent host — without enabling any scheduler yet — or, alternatively, proceed with due diligence/promotion review of the pending Binance USD-M Futures funding/open-interest candidate adapter (commit `418a52a`, not yet approved) as a second data source. Either path requires an explicit owner decision before `live_ingestion_allowed` or any scheduling is turned on.
