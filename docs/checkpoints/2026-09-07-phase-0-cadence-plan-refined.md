# Phase 0 Checkpoint — Cadence Rollout Plan Refined

Date: 2026-09-07
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Refine `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md` per the
owner's explicit choices this session, still without enabling any
automation or touching `live_ingestion_allowed`.

## SUMMARIZED STATE SHA

`f27a2c803dcfbfabc349694fbbd1730b1452c881`

This is the exact implementation state summarized by this checkpoint.

## WHAT CHANGED

- Updated `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`:
  - Recorded three owner decisions: use `launchd` (not `cron`) on this
    macOS host; enable FRED first and Coinbase only after a stable
    unattended period, not both at once; use a small read-only gap-check
    script instead of an alerting system.
  - Replaced the single "path to enabling" list with a two-stage rollout
    plan (Stage 1 FRED-only wrapper + `launchd` job + gap-check
    confirmation, Stage 2 add Coinbase wrapper + separate `launchd` job),
    each stage explicitly requiring its own future checkpoint and
    `live_ingestion_allowed` approval.
  - Added a gap-check report sketch (expected-vs-actual Coinbase hourly
    buckets and FRED business-day observations, read-only, print-only, no
    alerting integration) — sketch only, not implemented.
  - Retained the original open questions, marked resolved, for history.
- No adapter, ingestion, runtime, or schema code changed. No wrapper
  script, `launchd` plist, or gap-check script was created — this session
  produced design text only.

## VERIFIED

- `git fetch origin` then `git rev-parse main origin/main`: both equal
  `f27a2c803dcfbfabc349694fbbd1730b1452c881` before this session's edits —
  confirmed no drift before writing.
- `docker compose ps` on the persistent host: only `crypto-intelligence-db-1`
  running, `Up 13 hours (healthy)` — unchanged from the prior checkpoint,
  confirming no automation silently appeared.

## UNKNOWN

- The FRED `14:00 UTC` publish-time assumption is still unconfirmed against
  live FRED documentation — explicitly deferred to Stage 1, step 1 of the
  rollout plan, not resolved by this checkpoint.
- Exact US-holiday handling for the FRED gap-check's expected-business-day
  set is left as "to be decided when this is built," not specified here.
- How long "a stable unattended period" for FRED must run before Coinbase
  is added in Stage 2 is not numerically defined; left to the owner's
  judgment at that time.

## BLOCKERS

None. Documentation-only change.

## DECISIONS

- `launchd` is the approved automation mechanism for this host, superseding
  the undecided `cron`/`launchd` choice from the prior checkpoint.
- Cadence enablement is staged: FRED first, Coinbase strictly after, each
  with its own explicit owner approval and checkpoint — not a single
  combined activation.
- Gap detection at this scale is a manual, read-only report the owner runs
  themselves; no alerting system is planned unless volume later justifies
  it.
- None of the above starts any automation now; `live_ingestion_allowed`
  remains `false` and no scheduler exists yet.

## FILES CHANGED

- Updated `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`.
- Added this checkpoint file.
- Updated `CHECKPOINT_INDEX.json` and `PROJECT_STATE.json` pointers (see
  below).

## VALIDATION

Documentation-only; no automated test or CI run applies. `docker compose ps`
was used to confirm no drift in the live host state, cited above.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false`, unchanged.
- No `launchd` job, wrapper script, cron entry, or background process was
  created or loaded.
- No trading/execution.
- Only the already-approved Coinbase BTC-USD candles and FRED DGS2/DGS10
  are referenced; no new source touched.
- No secrets read, written, or referenced this session.

## ONE NEXT ACTION

Begin Stage 1 of the rollout plan only when the owner explicitly says to:
re-verify the FRED publish-time assumption against live FRED
documentation, then write `scripts/run_fred_cadence.sh` and a `launchd`
plist for it (not yet written), and bring both to a dedicated checkpoint
alongside the explicit `live_ingestion_allowed` decision for that one
source/cadence before loading the job. Do not start Stage 2 (Coinbase)
until Stage 1 has run unattended long enough for the owner to be
comfortable, per the plan in `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`.
