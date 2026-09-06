# Phase 0 Checkpoint — Binance Funding/OI Candidate Recorded

Date: 2026-09-06
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Close the end-of-session protocol gap left by the prior session's Binance USD-M
Futures funding-rate + open-interest candidate addition (commit `418a52a`),
which was applied via `git apply` outside Claude Code and pushed to `main`
without a checkpoint or `PROJECT_STATE.json` / `CHECKPOINT_INDEX.json` update.
This checkpoint does not change runtime state; it verifies and records what
already happened, and makes an explicit decision about what happens next.

## SUMMARIZED STATE SHA

`418a52a30ec12b37d04d933ff9f64fb42fdac6bb`

This is the exact implementation state summarized by this checkpoint. It was
committed and pushed in a prior session, before this checkpoint existed.

## WHAT CHANGED (prior session, already on `main` as of `418a52a`)

- Added CANDIDATE source `derivatives.binance.usdm_futures.btcusdt.funding_oi`
  (Binance USD-M Futures, public no-auth `fapi/v1/fundingRate` and
  `futures/data/openInterestHist`, `BTCUSDT` only).
- Added `src/adapters/binance_futures_funding_oi.py` (pure functions, no
  HTTP/DB inside the adapter, PIT-safe `raw_record_metadata`, matching the
  Coinbase/FRED adapter style).
- Added `tests/test_binance_futures_funding_oi.py` (12 write-free tests).
- Added `docs/architecture/BINANCE_FUTURES_FUNDING_OI_ADAPTER_v0.1.md` (full
  adapter contract, same shape as the Coinbase adapter contract).
- Added a `candidate` row and narrative section to
  `docs/architecture/DATA_SOURCE_REGISTRY.md` and
  `docs/architecture/SOURCE_DUE_DILIGENCE_v0.1.md`, explicitly flagged
  `PENDING APPROVAL`.
- Documented, as a known open item in both registry docs, that Binance's
  `futures/data/openInterestHist` retention window (~30 days observed) must be
  re-verified against live Binance documentation before approval, not assumed.

This session made none of the above changes; it verifies them and adds only
this checkpoint plus the pointer-file updates listed under FILES CHANGED.

## VERIFIED (this session)

- Cloned `mleontev111-max/crypto-intelligence` fresh and fetched full history
  (106 commits): `main` HEAD is exactly `418a52a30ec12b37d04d933ff9f64fb42fdac6bb`.
- Read `docs/architecture/DATA_SOURCE_REGISTRY.md` and
  `docs/architecture/SOURCE_DUE_DILIGENCE_v0.1.md` on that commit: the Binance
  funding/OI source is listed as `status: candidate`, decision
  `CANDIDATE / PENDING APPROVAL`; the approved Phase 0 pair is still exactly
  Coinbase BTC-USD candles + FRED DGS2/DGS10; the open-interest retention
  caveat is present and stated as unverified, not assumed resolved.
- Confirmed via the GitHub Actions API (independent of the prior session's
  self-report) that all three CI checks on commit `418a52a` are green:
  - `Market Adapter Guard` run #9 (id 34048118877) — `success`.
  - `Phase 0 Contract Guard` run #91 (id 34048118876) — `success`.
  - `Single-Node Runtime Guard` run #3 (id 34048118861) — `success`.
- Confirmed `PROJECT_STATE.json` on `418a52a` still has
  `live_ingestion_allowed: false` and had not been updated for this change
  (`current_checkpoint` and `one_next_action` still pointed at the prior
  2026-09-04 single-node-runtime checkpoint).

## UNKNOWN

- Whether the persistent-host deployment described in the prior checkpoint's
  `one_next_action` (deploy `compose.yml` on a persistent host, run one
  bounded manual Coinbase/FRED collection, restart the database container,
  and confirm the 3 RAW files / 30 observation / 30 lineage rows survive
  restart) has been performed anywhere outside this repository's CI. Asked
  the repo owner directly this session; the answer was "not sure / needs
  checking" — this is **not confirmed done** and **not confirmed pending**;
  treat it as still open until host evidence is produced and checkpointed.
- The exact current retention window for Binance
  `futures/data/openInterestHist` (documented as ~30 days observed, not yet
  re-verified against live Binance docs).

## BLOCKERS

- Cannot verify the persistent-host runtime step from this environment; it
  requires host access and evidence that only the repo owner can produce.
- No blocker on CI or code: all three guards are green on `main`.

## DECISIONS

- `derivatives.binance.usdm_futures.btcusdt.funding_oi` **stays `candidate`**.
  The repo owner explicitly chose not to open the due-diligence/approval gate
  this session. `live_ingestion_allowed` is untouched (`false`).
- Because the persistent-host deployment status is unconfirmed rather than
  confirmed complete, the original `one_next_action` from the 2026-09-04
  checkpoint remains authoritative and is carried forward unchanged, not
  replaced by an approval-gate task.
- This checkpoint's only repository changes are this file, `CHECKPOINT_INDEX.json`,
  and `PROJECT_STATE.json`'s `current_checkpoint` pointer; no adapter, ingestion,
  or runtime code was touched this session.

## FILES CHANGED (this session)

- `docs/checkpoints/2026-09-06-phase-0-binance-funding-oi-candidate-recorded.md` (new)
- `CHECKPOINT_INDEX.json` (new entry, superseded prior latest)
- `PROJECT_STATE.json` (`current_checkpoint` pointer only; `one_next_action`
  text unchanged)

## VALIDATION

- GitHub Actions run IDs above were read directly from the GitHub API this
  session, not taken from the prior session's report.
- Full commit history (`git rev-list --all --count` = 106) fetched and
  `main` HEAD SHA confirmed by direct `git rev-parse`.

## SAFETY BOUNDARIES

- `live_ingestion_allowed=false`, unchanged.
- No trading/execution.
- Only approved Coinbase BTC-USD candles and FRED DGS2/DGS10 may be ingested;
  Binance funding/OI remains adapter-and-tests-only, not wired into any
  ingestion path.
- FRED key remains runtime-only; no secret handling changed this session.

## ONE NEXT ACTION

Unchanged from the 2026-09-04 checkpoint, carried forward because its
completion is unconfirmed: deploy the validated `compose.yml` package on the
selected persistent host, create the host `.env` locally (without committing
it), start PostgreSQL, apply migrations, verify the collector is disabled by
default, run exactly one bounded manual Coinbase/FRED collection, restart the
database container, and verify that the 3 RAW files plus 3 RAW / 30
observation / 30 lineage database rows persist after restart; keep scheduling
off and keep `live_ingestion_allowed=false` until the resulting host evidence
is checkpointed. Report that host evidence back explicitly before this action
is marked verified — do not infer it from CI alone.
