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
- `revision_policy`: append_only / provider_revises / unknown
- `source_event_time_available`: yes / no / partial
- `provider_publish_time_available`: yes / no / partial
- `ingestion_time_recorded`: always yes in our system
- `raw_payload_retained`: required for approved sources unless licensing forbids it
- `license_or_terms_review`: pending / approved / blocked
- `expected_freshness`
- `failure_modes`
- `notes`

## Initial candidate registry

| source_id | category | provider | dataset | status | PIT rating | revision policy | notes |
|---|---|---|---|---|---|---|---|
| `market.binance.spot.btcusdt` | market | Binance | BTC/USDT trades/candles | candidate | conditional | provider_revises_or_unknown | Candidate market feed; exact endpoint and retention rules still to be reviewed. |
| `derivatives.coinglass.btc` | derivatives | CoinGlass | OI/funding/liquidations/taker flow | candidate | conditional | provider_revises_or_unknown | Aggregated derivatives candidate; exact historical semantics require verification. |
| `onchain.cryptoquant.btc` | onchain | CryptoQuant | exchange flow/reserve and selected BTC metrics | candidate | weak-to-conditional | provider_revises | Entity clustering can revise historical values; raw snapshots and `available_at` are mandatory. |
| `macro.fred.core` | macro | FRED | selected rates/macro series | candidate | conditional | provider_revises | Vintage/revision semantics must be handled; do not assume latest historical values were known earlier. |
| `news.curated.v0` | news | TBD | curated crypto/macro/regulatory news | candidate | unknown | source_specific | Must preserve first-seen, published and updated timestamps plus content hash. |

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

## Phase 0 rule

No live ingestion begins until the canonical schemas exist and at least one market source plus one non-market source have completed the approval gate.