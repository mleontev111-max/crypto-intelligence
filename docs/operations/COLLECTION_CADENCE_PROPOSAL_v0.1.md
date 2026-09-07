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

## Path to enabling this cadence (future, separate decision)

If the owner approves this design (as-is or amended), enabling it is a
distinct future step that should itself get its own checkpoint and
explicit `live_ingestion_allowed` decision, e.g.:

1. A small wrapper (host `cron`, or a `scripts/run_cadence_*.sh` invoked by
   `launchd`/`cron` on this Mac mini) that computes the window described
   above and calls the existing collector — no new ingestion logic.
2. Re-verify the FRED publish-time assumption against live FRED docs.
3. Add basic run logging/alerting so a silently-failing cadence is
   noticed.
4. Explicit owner approval to flip `live_ingestion_allowed` and start the
   scheduler, recorded in its own checkpoint with the exact mechanism
   enabled.

## Open questions for the owner

- Is hourly Coinbase / daily FRED the right cadence, or is a coarser
  cadence (e.g. every 4h for Coinbase, matching the shortest forecast
  horizon) preferable for Phase 0 to minimize footprint before Phase 1
  formally starts?
- Preferred automation mechanism on this host: `cron`, `launchd`, or defer
  until a proper scheduler service is justified?
- Who/what reviews cadence failures (missed runs, gaps) once enabled?
