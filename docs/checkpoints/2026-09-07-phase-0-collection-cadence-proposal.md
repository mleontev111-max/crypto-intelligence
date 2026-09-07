# Phase 0 Checkpoint — Collection Cadence Proposal Recorded

Date: 2026-09-07
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Address the first branch of the prior checkpoint's `one_next_action`: decide
and document a regular (but still explicitly bounded and reviewed)
collection-cadence proposal for Coinbase/FRED on the verified persistent
host, without enabling any scheduler and without touching
`live_ingestion_allowed`. The owner selected this branch (cadence proposal)
over the alternative (Binance candidate due diligence) this session.

## SUMMARIZED STATE SHA

`22e8699e0885c1235e1ba682fe364c78929b6b73`

This is the exact implementation state summarized by this checkpoint (the
commit that will carry this checkpoint's own files is necessarily a
descendant of it).

## WHAT CHANGED

- Added `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`: a
  design-only proposal for hourly Coinbase 1h-candle collection (4-bucket
  overlapping window) and daily FRED DGS2/DGS10 collection (10-day
  overlapping observation window), both expressed as explicit bounded
  windows reusing the already-verified collector entrypoint. The document
  explicitly states no scheduler exists yet, lists what it deliberately
  does not include (monitoring, auto-backfill, automation), and lays out
  the separate future steps and explicit approval required before any of
  it is enabled.
- No adapter, ingestion, runtime, or schema code changed. No container was
  started/stopped this session beyond a health re-check of the already
  running `db`.

## VERIFIED

- `git fetch origin` followed by `git rev-parse main origin/main`: both
  equal `22e8699e0885c1235e1ba682fe364c78929b6b73` before and is expected
  to match again immediately after this checkpoint is pushed — confirmed no
  state drift at session start (lesson applied from the prior session's
  stale-clone mistake).
- `docker compose ps` on the persistent host (`Mac-mini-Mihail.local`):
  only `crypto-intelligence-db-1` running, `Up 13 hours (healthy)` —
  confirms the database survived unattended since the last checkpoint with
  no scheduler or background collector process present.
- Re-read `ARCHITECTURE.md`, `ROADMAP.md`,
  `docs/architecture/COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`,
  `docs/architecture/FRED_H15_TREASURY_ADAPTER_v0.1.md`, and
  `docs/architecture/DATA_SOURCE_REGISTRY.md` to ground the proposed
  windows in the existing adapter contracts (bounded-window requirement,
  Coinbase's "must not be polled frequently" / 300-candle cap, FRED's
  `provider_revises` / explicit realtime-window requirement).

## UNKNOWN

- Whether hourly Coinbase / daily FRED is the cadence the owner actually
  wants, versus a coarser default (e.g. 4h Coinbase) — left as an open
  question in the proposal document for the owner to answer.
- The real FRED H.15 publication time is not re-verified against live FRED
  docs; the proposal explicitly flags `14:00 UTC` as an unconfirmed guess,
  matching the caution already used for the Binance OI retention window.
- Preferred host automation mechanism (`cron` vs `launchd` vs deferring)
  is unresolved and listed as an open question.

## BLOCKERS

None. This is a documentation-only proposal; it does not block or unblock
any runtime capability, and no code path depends on it.

## DECISIONS

- The owner chose to pursue the collection-cadence proposal now rather than
  the Binance funding/OI candidate due-diligence path; the Binance
  candidate (`derivatives.binance.usdm_futures.btcusdt.funding_oi`, commit
  `418a52a`) remains untouched, `status: candidate`, not approved.
- The cadence proposal is explicitly a document for review, not an
  activation. Enabling it (building the wrapper/scheduler, flipping
  `live_ingestion_allowed`) is deferred to a separate future checkpoint
  requiring explicit owner approval, per `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`'s
  own "Path to enabling this cadence" section.

## FILES CHANGED

- Added `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md`.
- Added this checkpoint file.
- Updated `CHECKPOINT_INDEX.json` and `PROJECT_STATE.json` pointers (see
  below).

## VALIDATION

Documentation-only change; no automated test or CI run applies. Validation
here consists of the design constraints being derived directly from the
already-verified, canonical adapter contracts and the current, live
`docker compose ps` state of the persistent host, both cited above.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false`, unchanged.
- No scheduler, cron, launchd job, or background collector process was
  created or started.
- No trading/execution.
- Only the already-approved Coinbase BTC-USD candles and FRED DGS2/DGS10
  are referenced by the proposal; no new source is touched.
- No secrets were read, written, or referenced this session.

## ONE NEXT ACTION

Owner reviews `docs/operations/COLLECTION_CADENCE_PROPOSAL_v0.1.md` and
either (a) approves the proposed hourly Coinbase / daily FRED cadence
as-is, (b) requests changes (e.g. a coarser Coinbase interval), or (c)
decides to defer cadence automation and pursue the Binance candidate
due-diligence path instead. Only after an explicit choice should a
follow-up session build the actual wrapper/scheduler and raise the
`live_ingestion_allowed` question in its own checkpoint.
