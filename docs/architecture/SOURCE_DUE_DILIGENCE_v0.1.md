# Phase 0 Source Due Diligence v0.1

**Status:** Canonical Phase 0 source-approval record.  
**Scope:** BTC Market Observatory, internal research only.  
**Live ingestion:** DISABLED.

## Approval rule

A source may be marked `approved` only for the exact dataset/use recorded here. Approval does not automatically authorize redistribution, public display, trading, account access, or a different dataset from the same provider.

## Decision matrix

| source_id | provider / dataset | access | semantics | PIT / revisions | terms / retention | cadence / limits | cost | decision |
|---|---|---|---|---|---|---|---|---|
| `market.coinbase.exchange.btcusd.candles` | Coinbase Exchange `BTC-USD` historic candles, REST `GET /products/BTC-USD/candles` | Public Exchange Market Data API; no trading/account auth required | OHLCV buckets. Supported granularities include 1m, 5m, 15m, 1h, 6h, 1d. Maximum 300 candles/request. Coinbase warns historical rates may be incomplete and no bucket is published when no ticks exist. | **conditional**. Bucket start is supplied, but no immutable-history guarantee is assumed. Record exact raw response plus first-seen/ingested/available timestamps; later changes append new evidence. | **APPROVED FOR INTERNAL RESEARCH ONLY.** Coinbase Market Data Terms permit limited internal/personal/research use; external redistribution/display/dissemination of Market Data or Derived Works requires separate review/permission. | Historical endpoint must not be polled frequently. Requests are deterministically paged at <=300 candles. | Public market-data endpoint; no source fee identified for this exact endpoint. | **APPROVED — internal Phase 0 read-only research** |
| `macro.fred.h15.dgs2_dgs10` | FRED / Board of Governors H.15 `DGS2`, `DGS10` | FRED API key, runtime secret only | Daily 2-year and 10-year Treasury constant-maturity yields, percent, not seasonally adjusted. FRED API supports real-time/vintage parameters. | **strong-to-conditional**. Explicit `realtime_start`/`realtime_end` and vintage semantics are available, but latest-history pulls must not be backdated. Revised values append new RAW evidence. | **APPROVED FOR THESE TWO SERIES ONLY.** Current FRED metadata identifies `DGS2` and `DGS10` as `Public Domain: Citation Requested`; FRED API terms/attribution requirements still apply. This is not blanket FRED approval. | Daily source series. API key required. Collection cadence must respect FRED/API behavior; no need for high-frequency polling. | No per-request source fee identified for this exact API use; runtime key required. | **APPROVED — internal Phase 0 read-only research** |
| `market.binance.spot.btcusdt` | Binance Spot `BTCUSDT` klines / public archive | Public market-data API / downloadable archives | Strong technical fit; Spot kline schema documented; public archive is daily/monthly and derived from Spot endpoints. | **conditional**. Public archive notes files can later be replaced after discovered issues, so immutable local snapshots/checksums are required. | **NOT APPROVED YET.** The official public-data repository states MIT, but public evidence does not resolve whether that license governs the archived data themselves; an official-repo issue requests clarification. | Public API is rate-limited; archive cadence is daily/monthly. | Public access; exact data-retention/commercial rights remain unresolved. | **CANDIDATE / LEGAL GAP** |
| `derivatives.coinglass.btc` | CoinGlass BTC derivatives | API/key/plan dependent | OI/funding/liquidations/taker-flow candidate. | Exact historical timestamp/revision semantics not yet reviewed in this gate. | Terms/retention not yet approved. | UNKNOWN pending endpoint-level review. | UNKNOWN pending current plan review. | **CANDIDATE** |
| `onchain.cryptoquant.btc` | CryptoQuant BTC exchange/on-chain metrics | API/key/plan dependent | Entity-labelled on-chain metrics. | **weak-to-conditional** by design: entity clustering can revise history. Raw point-in-time snapshots are mandatory. | Terms/retention not yet approved. | UNKNOWN pending current plan review. | UNKNOWN pending current plan review. | **CANDIDATE** |
| `news.curated.v0` | TBD | curated crypto/macro/regulatory news | Source-specific. | Must preserve first-seen, published, updated timestamps and content hashes. | UNKNOWN until exact publishers/feeds are selected. | UNKNOWN. | UNKNOWN. | **CANDIDATE** |

## Approved Phase 0 source pair

### Market

`market.coinbase.exchange.btcusd.candles`

Exact approved use:

- internal Crypto Intelligence research and Market Observatory development;
- read-only historic candles for `BTC-USD`;
- no trading/account/user endpoints;
- private RAW retention with content hash and first-seen/available timestamps;
- no external redistribution/display under this approval;
- 1h raw bars are the first collection candidate; any 4h bar is a later versioned causal derivation.

### Non-market / macro

`macro.fred.h15.dgs2_dgs10`

Exact approved use:

- `DGS2` and `DGS10` only;
- runtime API key supplied outside GitHub and never persisted in evidence metadata;
- explicit real-time/vintage request semantics where historical reconstruction matters;
- `.` remains missing, never silently interpolated;
- attribution/terms must be preserved for later product use.

## Why Binance is not first market source

Binance remains a priority technical candidate and better matches the originally planned `BTCUSDT` instrument. However, Phase 0 approval requires explicit dataset-use rights rather than technical convenience. Current public evidence leaves a material licensing ambiguity around downloadable archive data, so Binance remains candidate.

## Adapter contracts

- `docs/architecture/COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`
- `docs/architecture/FRED_H15_TREASURY_ADAPTER_v0.1.md`

## Sources reviewed on 2026-09-04

- Coinbase Exchange API introduction and historic-candles documentation.
- Coinbase Market Data Terms of Use.
- Binance Spot REST documentation and official `binance-public-data` repository/README plus licensing-clarification issue.
- FRED API Terms and observations/vintage documentation.
- FRED `DGS2` and `DGS10` series metadata/source-rights labels.

## Safety boundary

This document approves exact dataset definitions and internal read-only research use. It does **not** enable live ingestion. The strict Phase 0 gate remains: an approved market + non-market pair, adapter contracts, successful write-free adapter tests, and then a separate explicit checkpoint for any controlled network/write path. `PROJECT_STATE.live_ingestion_allowed` remains `false`.