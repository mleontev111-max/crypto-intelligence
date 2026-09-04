# Data Source Registry

Status: Phase 0 canonical design. No live ingestion is approved by this document.

## Purpose

Every external feed must be registered before ingestion so the system can reason about provenance, point-in-time safety, revisions, licensing, credentials, freshness and failure modes.

## Required registry fields

Each source entry must define:

- `source_id`
- `category`: market / derivatives / onchain / macro / news
- `provider`
- `dataset`
- `status`: candidate / approved / disabled
- `access_mode`: public / api_key / paid
- `point_in_time_rating`: strong / conditional / weak / unknown
- `revision_policy`: append_only / provider_revises / provider_revises_or_unknown / unknown
- `source_event_time_available`: yes / no / partial
- `provider_publish_time_available`: yes / no / partial
- `ingestion_time_recorded`: always yes in our system
- `raw_payload_retained`: required for approved sources unless licensing forbids it
- `license_or_terms_review`: pending / approved / blocked
- `expected_freshness`
- `failure_modes`
- `notes`

## Current registry

| source_id | category | provider | dataset | status | PIT rating | revision policy | notes |
|---|---|---|---|---|---|---|---|
| `market.coinbase.exchange.btcusd.candles` | market | Coinbase Exchange | `BTC-USD` historic REST candles | **approved** | conditional | provider_revises_or_unknown | Approved only for internal Phase 0 research/read-only use. Public/third-party display or redistribution is not approved. Adapter: `COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`. |
| `macro.fred.h15.dgs2_dgs10` | macro | FRED / Board of Governors | `DGS2`, `DGS10` daily Treasury constant-maturity yields | **approved** | strong-to-conditional | provider_revises | Approved only for these two series. FRED metadata identifies them as `Public Domain: Citation Requested`; FRED API terms and attribution requirements still apply. Adapter: `FRED_H15_TREASURY_ADAPTER_v0.1.md`. Runtime API key required; never persisted. |
| `market.binance.spot.btcusdt` | market | Binance | BTC/USDT trades/candles | candidate | conditional | provider_revises_or_unknown | Strong technical candidate, but archive/data licensing scope remains insufficiently resolved for our approval gate. |
| `derivatives.coinglass.btc` | derivatives | CoinGlass | OI/funding/liquidations/taker flow | candidate | conditional | provider_revises_or_unknown | Aggregated derivatives candidate; exact historical semantics and terms require verification. |
| `onchain.cryptoquant.btc` | onchain | CryptoQuant | exchange flow/reserve and selected BTC metrics | candidate | weak-to-conditional | provider_revises | Entity clustering can revise historical values; raw snapshots and `available_at` are mandatory. |
| `news.curated.v0` | news | TBD | curated crypto/macro/regulatory news | candidate | unknown | source_specific | Must preserve first-seen, published and updated timestamps plus content hash. |

## Approved Phase 0 pair

Market:

`market.coinbase.exchange.btcusd.candles`

Macro/non-market:

`macro.fred.h15.dgs2_dgs10`

Both approvals are narrow and internal/research-only. They do not authorize trading, account access, raw-data redistribution, or any unlisted dataset from the same providers.

See:

- `docs/architecture/SOURCE_DUE_DILIGENCE_v0.1.md`
- `docs/architecture/COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`
- `docs/architecture/FRED_H15_TREASURY_ADAPTER_v0.1.md`

## Approval gate

A candidate cannot become `approved` until we document:

1. exact dataset/endpoints;
2. timestamp semantics;
3. historical revision behavior;
4. retention/licensing constraints;
5. auth/security requirements;
6. expected rate limits and freshness;
7. how raw payloads are archived or, if prohibited, how evidence is preserved;
8. a read-only ingestion test plan.

## Phase 0 live-ingestion gate

Preserve the stricter original rule: **live ingestion remains disabled until at least one market source and at least one non-market source have both completed the approval gate**, their adapter contracts exist, and their write-free adapter tests pass.

That source-level condition is now satisfied by the approved Coinbase + FRED pair, but ingestion is **still disabled** until the current adapter guard passes on exact main and a separate checkpoint explicitly approves the controlled ingestion write path. No source or adapter may change `PROJECT_STATE.live_ingestion_allowed` implicitly.