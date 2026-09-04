# Phase 0 Source Due Diligence v0.1

**Status:** Canonical Phase 0 source-approval record.  
**Scope:** BTC Market Observatory, internal research only.  
**Live ingestion:** DISABLED.

## Approval rule

A source may be marked `approved` only for the exact dataset/use recorded here. Approval does not automatically authorize redistribution, public display, trading, account access, or a different dataset from the same provider.

## Decision matrix

| source_id | provider / dataset | access | semantics | PIT / revisions | terms / retention | cadence / limits | cost | decision |
|---|---|---|---|---|---|---|---|---|
| `market.coinbase.exchange.btcusd.candles` | Coinbase Exchange `BTC-USD` historic candles, REST `GET /products/BTC-USD/candles` | Public Exchange Market Data API; no trading/account auth required | OHLCV buckets. Supported granularities include 1m, 5m, 15m, 1h, 6h, 1d. Maximum 300 candles/request. Coinbase warns historical rates may be incomplete and no bucket is published when no ticks exist. | **conditional**. Bucket start is supplied, but Coinbase does not document an immutable historical-revision guarantee. We therefore record first-seen/ingested/available timestamps and retain the exact raw response used by the system. Later corrections must append, never rewrite prior evidence. | **APPROVED FOR INTERNAL RESEARCH ONLY.** Coinbase Market Data Terms grant a limited license for personal/research use by the entity and its officers/employees. Redistribution/display/dissemination of Market Data or Derived Works outside the organization is restricted without prior written consent. Raw retention is therefore internal only; public product use requires a new legal review. | Historical endpoint must not be polled frequently. Adapter must page time ranges at <=300 candles/request and obey published API/rate-limit behavior. | Public market-data access; no source fee identified for this exact public endpoint. Future paid/enhanced feeds are separate products and not approved here. | **APPROVED — internal Phase 0 research/read-only only** |
| `market.binance.spot.btcusdt` | Binance Spot `BTCUSDT` klines / public archive | Public market-data API / downloadable archives | Strong technical fit; Spot kline schema documented; public archive is daily/monthly and derived from `/api/v3/klines`. | **conditional**. Binance public archive explicitly notes archived files can later be replaced after discovered issues, so immutable local raw snapshots/checksums are required. | **NOT APPROVED YET.** The official `binance-public-data` repository states `MIT`, but it is not sufficiently clear from that statement alone whether the license governs the data archives themselves. An open official-repo issue specifically requests this clarification. | Public API is IP-rate-limited; archive daily data appears the next day and monthly data at start of next month. | Public access; exact commercial/retention terms remain unresolved. | **CANDIDATE / LEGAL GAP** |
| `derivatives.coinglass.btc` | CoinGlass BTC derivatives | API/key/plan dependent | OI/funding/liquidations/taker-flow candidate. | Exact historical timestamp/revision semantics not yet reviewed in this gate. | Terms/retention not yet approved. | UNKNOWN pending endpoint-level review. | UNKNOWN pending current plan review. | **CANDIDATE** |
| `onchain.cryptoquant.btc` | CryptoQuant BTC exchange/on-chain metrics | API/key/plan dependent | Entity-labelled on-chain metrics. | **weak-to-conditional** by design: entity clustering can revise history. Raw point-in-time snapshots are mandatory. | Terms/retention not yet approved. | UNKNOWN pending current plan review. | UNKNOWN pending current plan review. | **CANDIDATE** |
| `macro.fred.core` | FRED/ALFRED selected macro series | API key | Series observations with real-time/vintage parameters available. | **conditional**. Revision/vintage support is strong, but exact source series rights differ by series. | FRED API terms explicitly warn that individual series may be third-party copyrighted and impose attribution/other requirements. Therefore no blanket macro approval is granted; approve series-by-series. | API key required. Exact cadence depends on selected series. | API itself is available without an identified per-request fee, but terms still govern use. | **CANDIDATE / SERIES-BY-SERIES REVIEW** |

## First approved read-only dataset

`market.coinbase.exchange.btcusd.candles`

Exact approved use:

- internal Crypto Intelligence research and Market Observatory development;
- read-only historic candles for `BTC-USD` from Coinbase Exchange REST market-data API;
- no trading endpoints;
- no account/user data;
- no redistribution or public display of raw Coinbase Market Data or derived works under this approval;
- preserve raw response privately with content hash and first-seen/available timestamps;
- derived 4h research bars may be formed later from causal 1h bars, but that transformation must have its own versioned normalizer contract.

## Why Coinbase, not Binance, is first

Binance is the better match for the originally planned `BTCUSDT` instrument and remains a priority candidate. However, Phase 0 rules require explicit terms/retention approval rather than technical convenience. The current public evidence leaves a material licensing ambiguity around downloadable archive data, so Binance remains candidate until that gap is resolved.

## Sources reviewed on 2026-09-04

- Coinbase Exchange API introduction and historic-candles documentation.
- Coinbase Market Data Terms of Use (internal/research license and redistribution restrictions).
- Binance Spot REST documentation and official `binance-public-data` repository/README.
- FRED API Terms and observations/vintage documentation.

## Safety boundary

This document approves a dataset definition, **not live ingestion**. `PROJECT_STATE.live_ingestion_allowed` remains `false` until the adapter contract is committed, reviewed, and a write-free adapter test is implemented.