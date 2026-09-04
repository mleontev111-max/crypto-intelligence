# Phase 0 Checkpoint — FRED Live Probe Verified

Date: 2026-09-04
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Close the explicit FRED runtime-secret/live-probe gate without enabling live ingestion, and establish the next safe boundary for RAW-first PostgreSQL ingestion design.

## SUMMARIZED STATE SHA

`1fcd96f3988f438b422fbcfacc7e7296ba3ea352`

This is the exact implementation/research state summarized by this checkpoint. Checkpoint/pointer-only commits may be descendants.

## WHAT CHANGED / VERIFIED

- `FRED_API_KEY` is configured as a GitHub Actions runtime secret; the value is not committed.
- Market Adapter Guard rerun completed successfully on the source-probe implementation commit `1982b38bfb7f191503c4cb7e64cf7c27802e969b`.
- The workflow environment masked `FRED_API_KEY` as `***`.
- Coinbase BTC-USD live zero-write probe returned HTTP 200.
- FRED `DGS2` live zero-write probe returned HTTP 200; safe evidence URL redacted `api_key=REDACTED`; parsed 13,110 records; response SHA-256 `ee733e34f5a12ee954c7579f1de72bb5df5f813ada144f936dd94d61d719fea9`.
- FRED `DGS10` live zero-write probe returned HTTP 200; safe evidence URL redacted `api_key=REDACTED`; parsed 16,870 records; response SHA-256 `5d853e5cdfed17c9700acb08af7ed5b8ee5a9107dab86b0512382c1fc6d9a77a`.
- All 15 deterministic adapter/transport tests passed in that workflow rerun.
- The source-probe guard still asserts no DB/trading client imports and no committed literal credentials in the probe surface.
- Research Memo v0.3 was archived at `docs/research/2026-09-04-inference-stability-target-robustness-v0.3.md` as `RESEARCH / NOT YET CANONICAL`; it does not change production policy.
- Phase 0 Contract Guard completed successfully on exact summarized state SHA `1fcd96f3988f438b422fbcfacc7e7296ba3ea352`.

## VERIFIED BOUNDARY

The approved Coinbase and FRED source adapters have now demonstrated live read-only connectivity and evidence generation. This verifies source access; it does NOT authorize database ingestion.

## UNKNOWN

- The exact RAW-first ingestion transaction API/implementation has not been designed or tested.
- Idempotency semantics across repeated provider payloads and revisions need explicit implementation tests.
- The boundary between raw payload persistence and normalized observations needs an atomic failure/rollback contract.
- Controlled ingestion has not been exercised against PostgreSQL.
- The evaluation recommendations in Research Memo v0.3 remain research input, not canonical model policy.

## BLOCKERS

No blocker to designing and testing RAW-first ingestion on deterministic fixtures / ephemeral PostgreSQL.

Live ingestion remains intentionally blocked until the ingestion transaction is implemented, tested for atomicity/idempotency/PIT provenance, and accepted in a later checkpoint.

## DECISIONS

- Keep `live_ingestion_allowed = false`.
- Never store or log the FRED API key.
- Preserve raw provider response bytes/hash/provenance before deriving observations.
- A normalized observation may not exist without traceable immutable RAW evidence.
- Repeated ingestion of the same source response must be idempotent rather than creating duplicate RAW/observation facts.
- Provider revisions must be represented append-only; prior RAW evidence must not be overwritten.
- Failure after RAW staging but before normalized observation completion must not leave a falsely complete ingestion unit.

## SAFETY BOUNDARIES

- No trading or exchange-account execution.
- No live database ingestion yet.
- No secret persistence.
- No mutation/deletion of immutable RAW evidence.
- No automatic canonicalization of research recommendations.

## ONE NEXT ACTION

Design and implement a fixture-driven RAW-first PostgreSQL ingestion transaction for the approved Coinbase BTC-USD candle and FRED DGS2/DGS10 adapter outputs, with immutable raw-event provenance, content-hash idempotency, PIT-safe `available_at`, append-only revision handling, atomic RAW-to-observation linkage, and rollback/failure tests in ephemeral PostgreSQL; keep all network-to-database live ingestion disabled and keep `live_ingestion_allowed=false` until a later checkpoint explicitly authorizes a controlled ingestion run.