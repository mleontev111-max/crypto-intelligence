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
| `market.coinbase.exchange.btcusd.candles` | market | Coinbase Exchange | `BTC-USD` historic REST candles | **approved** | conditional | provider_revises_or_unknown | **Approved only for internal Phase 0 research/read-only use.** Public/third-party display or redistribution is not approved. Exact adapter contract: `COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`. Live ingestion remains disabled. |
| `market.binance.spot.btcusdt` | market | Binance | BTC/USDT trades/candles | candidate | conditional | provider_revises_or_unknown | Strong technical candidate, but archive/data licensing scope remains insufficiently resolved for our approval gate. |
| `derivatives.coinglass.btc` | derivatives | CoinGlass | OI/funding/liquidations/taker flow | candidate | conditional | provider_revises_or_unknown | Aggregated derivatives candidate; exact historical semantics and terms require verification. |
| `onchain.cryptoquant.btc` | onchain | CryptoQuant | exchange flow/reserve and selected BTC metrics | candidate | weak-to-conditional | provider_revises | Entity clustering can revise historical values; raw snapshots and `available_at` are mandatory. |
| `macro.fred.core` | macro | FRED | selected rates/macro series | candidate | conditional | provider_revises | Vintage/revision support exists, but licensing/ownership is series-specific; no blanket approval. |
| `news.curated.v0` | news | TBD | curated crypto/macro/regulatory news | candidate | unknown | source_specific | Must preserve first-seen, published and updated timestamps plus content hash. |

## First approved dataset

`market.coinbase.exchange.btcusd.candles`

Approval scope is intentionally narrow:

- Coinbase Exchange public Market Data REST candles;
- `BTC-USD` only;
- internal research / Market Observatory development only;
- read-only requests only;
- no account, user, order, transfer or wallet access;
- private raw retention with provenance/hash;
- no external redistribution/display under this approval;
- live ingestion still disabled until the broader Phase 0 gate below is satisfied.

See:

- `docs/architecture/SOURCE_DUE_DILIGENCE_v0.1.md`
- `docs/architecture/COINBASE_BTCUSD_CANDLES_ADAPTER_v0.1.md`

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

Approval of Coinbase as the first market dataset is necessary but **not sufficient** to enable ingestion. A later checkpoint must explicitly change `PROJECT_STATE.live_ingestion_allowed`; no adapter or source approval may change that flag implicitly.