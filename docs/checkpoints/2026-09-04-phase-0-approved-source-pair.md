# Phase 0 Approved Source Pair Checkpoint

**Date:** 2026-09-04  
**Phase:** 0 — Foundation  
**Status:** ACTIVE  
**Summarized state SHA:** `c60dd241148e9aa8152310d5de9f9163f56e2043`

## GOAL

Complete source-by-source due diligence for the first BTC Market Observatory inputs, approve one market and one non-market dataset for narrow internal read-only research use, define adapter contracts, and prove their adapters are write-free before any live ingestion is allowed.

## WHAT CHANGED

- Added canonical source due diligence and approval matrix.
- Approved `market.coinbase.exchange.btcusd.candles` for internal Phase 0 read-only research only.
- Approved `macro.fred.h15.dgs2_dgs10` for exact `DGS2`/`DGS10` internal Phase 0 read-only research only.
- Kept Binance Spot BTCUSDT as candidate because archive/data licensing scope remains unresolved for our approval gate.
- Kept CoinGlass, CryptoQuant and curated news as candidates pending endpoint/terms/PIT review.
- Added versioned Coinbase and FRED adapter contracts.
- Added pure Python write-free adapter primitives and fixture tests.
- Added Market Adapter Guard covering both approved adapters, absence of DB/trading imports and literal committed credential values.
- Preserved the stricter multi-source live-ingestion gate.

## VERIFIED

- Market Adapter Guard on source-pair implementation state `743e6523f373448924467eeef2e2bc547a36c203`: **SUCCESS**.
- Phase 0 Contract Guard on `743e6523f373448924467eeef2e2bc547a36c203`: **SUCCESS**.
- Final canonical due-diligence document update at summarized state `c60dd241148e9aa8152310d5de9f9163f56e2043` changed documentation only; Phase 0 Contract Guard on that exact state: **SUCCESS**.
- Coinbase adapter is restricted to `BTC-USD` Exchange candles and performs no network or DB operation by itself.
- Coinbase tests preserve first-seen `available_at`, reject invalid OHLC/duplicates and do not silently manufacture unsupported native 4h bars.
- FRED adapter allows only `DGS2`/`DGS10`, keeps API key outside safe persisted metadata and preserves `.` as missing.
- `PROJECT_STATE.live_ingestion_allowed` remains `false`.
- Paper trading and live trading remain disabled.

## UNKNOWN

- No controlled real-network probe has yet been performed for either approved source.
- HTTP retry/backoff/timeout/response-capture transport is not implemented.
- FRED runtime API key is not configured in this repository and must remain external to GitHub.
- Binance archive data-license scope remains unresolved.
- CoinGlass/CryptoQuant exact terms, current pricing and PIT/revision semantics are not approved.
- News source selection is still open.
- Target semantics for DOWN/RANGE/UP remain research/open.

## BLOCKERS

No blocker for building a **read-only network probe with zero database writes** for the approved Coinbase and FRED adapters. Controlled ingestion into PostgreSQL remains blocked until network behavior, evidence capture, secret handling and write-path transaction semantics are independently tested and explicitly approved.

## DECISIONS

- Dataset approval is provider+dataset+use-specific, never blanket provider approval.
- Coinbase is the first market source despite Binance being closer to the planned BTCUSDT instrument because rights/terms certainty is part of the architecture gate.
- FRED approval is limited to `DGS2` and `DGS10`; generic FRED series remain unapproved until series-level rights review.
- Historical vendor event timestamps never backdate system `available_at` automatically.
- API credentials are runtime secrets and never RAW evidence metadata.
- Write-free adapter success does not implicitly enable ingestion.

## FILES CHANGED

- `docs/architecture/SOURCE_DUE_DILIGENCE_v0.1.md`
- `docs/architecture/DATA_SOURCE_REGISTRY.md`
- `docs/architecture/COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`
- `docs/architecture/FRED_H15_TREASURY_ADAPTER_v0.1.md`
- `src/adapters/coinbase_exchange_candles.py`
- `src/adapters/fred_h15_treasury.py`
- `tests/test_coinbase_exchange_candles.py`
- `tests/test_fred_h15_treasury.py`
- `.github/workflows/market-adapter-guard.yml`
- this checkpoint.

## VALIDATION

- Market Adapter Guard: SUCCESS on the finalized source-pair implementation state before documentation-only due-diligence finalization.
- Phase 0 Contract Guard: SUCCESS on exact summarized state `c60dd241148e9aa8152310d5de9f9163f56e2043`.

## SAFETY BOUNDARIES

No live ingestion, no database writes from adapters, no exchange credentials, no account/order endpoints, no paper trading, no live trading, no public redistribution approval, no production model promotion.

## ONE NEXT ACTION

Implement and test a controlled **read-only HTTP source probe** for the approved Coinbase BTC-USD candles and FRED DGS2/DGS10 adapters that performs zero database writes, uses explicit timeout/retry/rate-limit handling, computes raw response hashes and evidence metadata, proves FRED secrets are never persisted/logged, and records source-response semantics. Only after both probes are verified should a later checkpoint design the controlled PostgreSQL ingestion transaction; keep `live_ingestion_allowed=false`.