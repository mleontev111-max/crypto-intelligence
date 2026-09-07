# Collection Cadence Proposal v0.1

**Status: PROPOSAL ONLY. Not enabled. No scheduler exists in this repository as of this document.**

This document specifies a candidate regular collection cadence for the two
approved Phase 0 sources (`market.coinbase.exchange.btcusd.candles` and
`macro.fred.h15.dgs2_dgs10`) so the owner can review and explicitly approve
(or amend) it before any automation is built. Writing or approving this
document does not itself change `PROJECT_STATE.live_ingestion_allowed`,
does not start a scheduler, and does not authorize any collection beyond
what is already independently verified: manual, bounded, explicitly
invoked runs of the existing collector.

## Why a cadence is needed at all

`forecast_horizons_planned` is `4h / 24h / 7d`. Building reliable features
for those horizons needs continuous, gap-tracked market data rather than
one-off manual pulls. Roadmap Phase 1 ("Market Observatory") exit gate is
explicitly "stable collection with observable gaps/quality metrics and
reproducible snapshots" — this proposal is preparation for that gate, not
an announcement that Phase 1 has started.

## Design constraints carried over from the adapter contracts

- Every collection call must remain an **explicit bounded window** — no
  open-ended or "since last run, whatever that means" requests
  (`COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`, `FRED_H15_TREASURY_ADAPTER_v0.1.md`).
- Coinbase: "the historical endpoint must not be polled frequently," and
  max 300 candles/request. `provider_revises_or_unknown` — a re-fetched
  bucket that returns different bytes must create new RAW evidence, never
  overwrite.
- FRED: `DGS2`/`DGS10` are daily, business-day, `provider_revises` series.
  `realtime_start`/`realtime_end` must be carried explicitly on every call;
  a "latest" pull must never be treated as proof a revised value was known
  earlier.
- All collection is already idempotent by deterministic IDs / content hash
  (verified in `docs/checkpoints/2026-09-06-phase-0-persistent-host-runtime-verified.md`),
  so an overlapping re-request of unchanged data is a no-op, not a
  duplicate-row risk.

## Proposed cadence

### Coinbase BTC-USD 1h candles

- **Frequency:** once per hour, a few minutes after the top of the UTC
  hour (e.g. `:05`), to give Coinbase time to finalize the just-completed
  1h bucket.
- **Window:** `[floor(now, 1h) − 4h, floor(now, 1h))` — the last 4 completed
  1h buckets, not just the newest 1.
  - Rationale: this is a deliberate overlap, not a mistake. It absorbs (a)
    a bucket Coinbase revises shortly after close, and (b) a missed run of
    up to ~3 hours (host restart, transient network failure) without
    leaving a silent gap, since idempotency makes the overlap free.
  - 4 buckets is far under the 300-per-request cap, so this does not
    conflict with the "don't poll frequently" rule — it is a small, fixed,
    predictable request shape, not deep-history scraping.
- **Deep backfill** (a gap wider than 4h — e.g. the host was down over a
  weekend) is explicitly **not** auto-healed by this cadence. It requires
  a separate, manually invoked, explicitly bounded backfill window using
  the same collector, reviewed like any other manual run — never an
  unbounded request.

### FRED DGS2 / DGS10

- **Frequency:** once per day. Proposed time: `14:00 UTC`, chosen as a
  conservative guess that the prior business day's H.15 value has been
  published; **the exact FRED publication schedule must be re-confirmed
  against live FRED documentation before this is ever automated** — same
  caveat style already used for the Binance OI retention window in
  `DATA_SOURCE_REGISTRY.md`, not assumed here either.
- **Window:** `realtime_date = today (UTC)`; `observation_start = today − 10
  calendar days`; `observation_end = today`.
  - Rationale: a 10-day lookback safely spans weekends and the longest
    plausible US market holiday without missing a business day, and lets
    late FRED revisions to recent observations be captured automatically.
    Idempotency again makes the overlap free.

### Common shape

Every run — whether Coinbase or FRED — is exactly one more invocation of
the already-verified collector entrypoint
(`docker compose --profile manual run --rm collector --write ...`) with a
freshly computed, fully explicit, bounded `start`/`end` (and for FRED,
`realtime_date`). No new adapter or ingestion code is required for this
proposal; only orchestration (see below) would be new, and none is built
yet.

## What this proposal does **not** include

- No scheduler, cron entry, systemd timer, launchd job, or background
  process exists yet. `docker compose ps` on this host shows only `db`
  running; `migrate` and `collector` remain under the `manual` Compose
  profile.
- No change to `PROJECT_STATE.live_ingestion_allowed` (`false`).
- No monitoring/alerting or gap-detection query has been built. A future
  task should add a report that flags missing expected Coinbase hourly
  buckets or missing FRED business-day observations against this cadence's
  expected shape — tracked as follow-up, not implemented here.
- No automatic historical backfill beyond the bounded windows above.

## Decisions (owner-approved this session, 2026-09-07)

The owner reviewed the open questions below and approved this cadence
design with three refinements. **These are still design decisions, not an
activation** — nothing in this section starts a scheduler or touches
`live_ingestion_allowed`; it narrows *how* enabling would happen, when a
future session actually does it.

1. **Automation mechanism: `launchd`, not `cron`.** This is a single macOS
   host. Modern macOS increasingly restricts `cron` behind Full Disk Access
   / TCC prompts that can silently break a job with no obvious error,
   whereas `launchd` is the native scheduling mechanism, handles sleep/wake
   more predictably, and needs no special permission grant for a job that
   just runs `docker compose`.
2. **Staged rollout, not both sources at once.** Enable **FRED first**
   (low frequency — once/day — easy to eyeball manually for a few days),
   let it run unattended for a period the owner is comfortable with, and
   only then enable **Coinbase** (higher frequency, more surface for a
   silent failure to hide in). Do not flip both on in the same step.
3. **Gap-checking: one small report script, not an alerting system.** Phase
   0 does not need push alerts. A short read-only script that prints
   expected-vs-actual buckets is enough to satisfy Phase 1's "observable
   gaps" exit criterion at this scale; see the sketch below.

## Path to enabling this cadence (future, separate decision)

Enabling any part of this is still a distinct future step requiring its
own checkpoint and an explicit `live_ingestion_allowed` decision. With the
refinements above, the concrete sequence would be:

**Stage 1 — FRED only**

1. Re-verify the `14:00 UTC` FRED publish-time assumption against live FRED
   documentation (still unconfirmed as of this document).
2. Add a small wrapper script (e.g. `scripts/run_fred_cadence.sh`) that
   computes `realtime_date`/`observation_start`/`observation_end` per the
   window above and calls
   `docker compose --profile manual run --rm collector --write ...` with
   only the FRED flags — Coinbase flags stay out of this script entirely
   in Stage 1.
3. Install a `launchd` `LaunchAgent`/`LaunchDaemon` plist with a
   `StartCalendarInterval` of once daily, pointed at that wrapper (plist
   not written yet — this is the design, not the file).
4. Explicit owner approval to flip `live_ingestion_allowed` for this one
   source/cadence and load the `launchd` job, recorded in its own
   checkpoint naming the exact plist and wrapper path enabled.
5. Run the gap-check script (below) daily for a few days and have the
   owner confirm no unexplained gaps before moving to Stage 2.

**Stage 2 — add Coinbase**

6. Add `scripts/run_coinbase_cadence.sh` (hourly, 4-bucket window, same
   shape as the FRED wrapper) and its own `launchd` job
   (`StartCalendarInterval` hourly at minute 5).
7. Separate explicit owner approval and checkpoint before this job is
   loaded — Stage 1 approval does not carry over to Stage 2.
8. Extend the gap-check script to cover expected hourly Coinbase buckets
   (sketch below already includes both).

Nothing in Stage 1 or Stage 2 is built or installed yet; both remain
future work pending the trigger described above.

## Gap-check report (sketch, not implemented)

A single read-only script/query — no alerting integration, run manually or
by its own daily `launchd` tick that just prints to a log — comparing
expected vs. actual coverage:

- **Coinbase:** for a lookback window (e.g. last 7 days), generate the set
  of expected `bucket_start` timestamps at 1h steps and `EXCEPT` against
  distinct observed bucket timestamps already in `observations` for
  `market.coinbase.exchange.btcusd.candles` — any remainder is a gap to
  print.
- **FRED:** for the same lookback window, generate the set of expected
  US business days (weekdays, minus a static or simply-approximated
  US-holiday list — exact holiday handling to be decided when this is
  built) and `EXCEPT` against distinct observed observation dates per
  series (`DGS2`, `DGS10`) already in `observations` — any remainder is a
  gap to print.
- Output: plain text/JSON list of missing buckets/dates per source, printed
  to stdout/log. No database writes, no external notification — reading
  this is the owner's job at this stage, consistent with "one small script,
  not an alerting system" above.
- This script is read-only against already-ingested data; it requires no
  new adapter code and does not itself perform any network fetch.

## Open questions (resolved above) — kept for history

- ~~Is hourly Coinbase / daily FRED the right cadence, or coarser?~~ →
  cadence approved as originally proposed; sequencing (not frequency) is
  what changed.
- ~~Preferred automation mechanism?~~ → `launchd`.
- ~~Who/what reviews cadence failures?~~ → the owner, manually, via the
  gap-check script above, at this scale — revisit if/when volume justifies
  real alerting.
