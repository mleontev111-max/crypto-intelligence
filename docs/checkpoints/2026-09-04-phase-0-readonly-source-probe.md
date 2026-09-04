# Phase 0 Read-Only Source Probe Checkpoint

**Date:** 2026-09-04  
**Phase:** 0 — Foundation  
**Status:** ACTIVE  
**Summarized state SHA:** `1982b38bfb7f191503c4cb7e64cf7c27802e969b`

## GOAL

Add and verify a constrained real-network probe layer for approved sources without enabling database writes or trading/account access.

## WHAT CHANGED

- Added `src/transport/read_only_http.py`: HTTPS GET only, approved-host allowlist, explicit timeout, bounded retry policy, SHA-256 evidence, and query-secret redaction.
- Added deterministic transport tests.
- Added `scripts/probe_approved_sources.py` for safe Coinbase/FRED live probes that emit sanitized evidence only.
- Expanded Market Adapter Guard to test adapters + transport, scan for DB/trading imports and literal credentials, and perform a real zero-write Coinbase probe.
- Added conditional FRED DGS2/DGS10 live probes using runtime-only `FRED_API_KEY` if configured.
- Added canonical `READ_ONLY_SOURCE_PROBE_v0.1.md` safety/evidence contract.

## VERIFIED

- Market Adapter Guard on implementation commit `e6a7672881890629e0fd843c96506a6483864038`: **SUCCESS**.
- 15 deterministic adapter/transport tests: **PASS**.
- Static checks found no PostgreSQL/SQLAlchemy/trading endpoint imports and no committed credential-like literals in source-probe code.
- Live Coinbase zero-write probe: **SUCCESS**, HTTP 200, 1 attempt, 4 parsed records, 242 response bytes, content type `application/json; charset=utf-8`, SHA-256 `7dadbe88f945b05467a3232c471859175ef0b018202f427b0ccc4666d1340640`.
- Market Adapter Guard on exact summarized state `1982b38bfb7f191503c4cb7e64cf7c27802e969b`: **SUCCESS**.
- On that exact state the Coinbase live probe repeated successfully with the same fixed-range response hash and 4 parsed records.
- FRED live-probe step executed safely but explicitly reported `SKIPPED: FRED_API_KEY runtime secret is not configured`; no fallback endpoint was used.
- Phase 0 Contract Guard on exact summarized state `1982b38bfb7f191503c4cb7e64cf7c27802e969b`: **SUCCESS**.
- `live_ingestion_allowed` remains `false`.

## UNKNOWN

- Real FRED DGS2 and DGS10 API response semantics through our live transport are not yet verified because the runtime secret is absent.
- No PostgreSQL ingestion transaction/write service exists yet.
- Network response evidence is not persisted during probes by design.
- Provider outage/rate-limit behavior has only deterministic transport coverage, not long-running operational evidence.
- Target semantics for DOWN/RANGE/UP remain research/open.

## BLOCKERS

The current ONE NEXT ACTION requires a valid FRED API key configured as GitHub Actions secret `FRED_API_KEY`. The key must not be pasted into repository files, checkpoint text, logs, issue comments, or chat-generated code.

No blocker exists for further offline design, but controlled PostgreSQL ingestion remains gated on successful FRED live probes under the current protocol.

## DECISIONS

- Real connectivity is tested before any database write path is designed.
- Source probe transport is host-allowlisted and GET-only rather than a general HTTP client.
- Raw bytes are hashed but not persisted by the Phase 0 probe.
- Secret-bearing request URLs are sanitized before evidence emission.
- Missing FRED secret causes an explicit skip, never a silent fallback or credential workaround.
- Live Coinbase success does not authorize ingestion.

## FILES CHANGED

- `src/transport/read_only_http.py`
- `tests/test_read_only_http.py`
- `scripts/probe_approved_sources.py`
- `.github/workflows/market-adapter-guard.yml`
- `docs/architecture/READ_ONLY_SOURCE_PROBE_v0.1.md`
- this checkpoint.

## VALIDATION

- Market Adapter Guard: SUCCESS on exact summarized state.
- Phase 0 Contract Guard: SUCCESS on exact summarized state.
- Coinbase real read-only network probe: SUCCESS.
- FRED real network probe: NOT RUN — runtime secret absent, explicitly reported by CI.

## SAFETY BOUNDARIES

No database writes, no RAW persistence, no exchange credentials, no account/order endpoints, no trading, no paper trading, no live ingestion, no public redistribution approval, no secret logging.

## ONE NEXT ACTION

Configure a valid FRED API key as the repository/runtime GitHub Actions secret named `FRED_API_KEY` (never commit or paste it into project files), then re-run the existing Market Adapter Guard and verify live zero-write probes for both `DGS2` and `DGS10`, including secret redaction and response hashes. Only after both FRED probes succeed should a later checkpoint design the controlled RAW-first PostgreSQL ingestion transaction; keep `live_ingestion_allowed=false`.