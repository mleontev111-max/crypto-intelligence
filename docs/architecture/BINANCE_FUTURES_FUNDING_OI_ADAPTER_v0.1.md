# Binance USD-M Futures Funding Rate + Open Interest Adapter Contract v0.1

**Status:** Canonical adapter contract; implementation not yet enabled.
**Source ID:** `derivatives.binance.usdm_futures.btcusdt.funding_oi`
**Mode:** read-only / internal research only.
**Live ingestion:** DISABLED.

## Why this source

Phase 0 approved a market source (Coinbase candles) and a macro source (FRED DGS2/DGS10), both
low-frequency relative to the project's intraday/swing (hours-to-days) forecast horizon. Neither
funding rate nor open interest is represented in the approved pair. This adapter closes that gap
with the narrowest public, no-auth Binance USD-M Futures endpoints for `BTCUSDT`.

This is a new candidate, not yet an approved source. It must pass the same Data Source Registry
approval gate as Coinbase/FRED (`docs/architecture/DATA_SOURCE_REGISTRY.md`,
`docs/architecture/SOURCE_DUE_DILIGENCE_v0.1.md`) before any write path is enabled.

## Endpoints

Binance USD-M Futures public Market Data (no API key, no account/order/trading authentication):

- `GET https://fapi.binance.com/fapi/v1/fundingRate` — historical settled funding rate.
- `GET https://fapi.binance.com/futures/data/openInterestHist` — historical open interest.

Approved request parameters:

- `symbol` (must be `BTCUSDT` only)
- `startTime`, `endTime`
- `limit`
- `period` (open interest only)

Adapter must never call account, order, position, transfer, wallet, listenKey, or any
signed/authenticated endpoint. No API secret or HMAC signing is implemented or required by this
adapter.

## Dataset semantics

### Funding rate (`fapi/v1/fundingRate`)

Each row: `symbol`, `fundingRate` (decimal string), `fundingTime` (epoch ms, settlement time),
`markPrice`. Default `limit` is 100, maximum is 1000. History is available back to contract
launch; no short retention window is documented for this endpoint.

### Open interest history (`futures/data/openInterestHist`)

Each row: `symbol`, `sumOpenInterest`, `sumOpenInterestValue`, `timestamp` (epoch ms). Canonical
raw collection candidate: `period=1h`, `limit<=500`. **This endpoint has a short retention
window, historically observed to be on the order of 30 days of history.** Unlike funding rate,
open interest history cannot be backfilled arbitrarily far; late collection start means permanent
gaps for the missed window. This must be recorded as an explicit quality/coverage limitation, not
silently treated as equivalent to funding rate's longer availability.

## Point-in-time contract

For every HTTP response, store a RAW record with:

- `source_id = derivatives.binance.usdm_futures.btcusdt.funding_oi`;
- `dataset` field distinguishing `funding_rate` vs `open_interest_hist` (same source_id, two
  dataset types, since both come from the same provider/instrument approval);
- request URL/parameters in metadata;
- exact response bytes/object reference;
- `observed_at` = collector receive/observation time;
- `ingested_at` = durable persistence time;
- `available_at` = no earlier than the system's first defensible observation time for that
  returned payload;
- content hash;
- schema version.

`fundingTime` / `timestamp` are `source_event_at`, not proof the historical value was known to our
system at that old timestamp, identical in spirit to the Coinbase candle contract. Historical
backfills retain collection-time `available_at`.

## Revision policy

`provider_revises_or_unknown`. No immutable-history guarantee is assumed for either dataset.
Re-fetching a historical range that yields changed content creates new RAW evidence; never update
an existing payload in place.

## Pagination / request discipline

- Funding rate: partition requested history into windows of `<=1000` rows using `startTime` /
  `endTime`, paging forward from the last returned `fundingTime + 1`.
- Open interest: partition into windows of `<=500` rows using `startTime` / `endTime`; do not
  request further back than the provider's actual retained history, and record an explicit
  `coverage_start_unknown` quality flag rather than assuming absence of older data means zero
  open interest.
- Respect Binance's published request weight limits; retry `429`/`5xx` conservatively with
  bounded exponential backoff; no infinite retry loops.
- Record HTTP status and response metadata for failed attempts separately from successful RAW
  payloads.

## Normalization contract

A successful raw row may normalize into one observation only after validation:

- `symbol == "BTCUSDT"`;
- `fundingRate` / `sumOpenInterest` parse as valid decimals;
- `sumOpenInterest >= 0`;
- timestamp is a plausible epoch-ms value within the requested window;
- duplicate raw payload lineage is preserved rather than hidden.

Quality flags must represent gaps or suspect data, in particular the open interest retention
boundary above. Silent interpolation is forbidden.

## Terms boundary

Binance API Terms of Use govern this public market-data use. Approval here is limited to internal
research use for `BTCUSDT` funding rate and open interest only. No trading, account, or user-data
endpoints are in scope. Any end-user/public application use requires a fresh terms/legal review.

## Write-free adapter test required before enabling ingestion

The first implementation must run in a no-database-write fixture/test mode and prove:

1. exact endpoints and `BTCUSDT` only;
2. funding rate request window `<=1000` rows, open interest window `<=500` rows;
3. response parser semantics for both datasets;
4. timestamp separation (`source_event_at` vs `available_at`);
5. content hashing;
6. gap preservation, including the open interest retention boundary;
7. no credentials/signed/order methods present;
8. no database writes or live-ingestion flag changes.

Only after that test passes may the project consider a separate checkpoint to permit controlled
ingestion, following the same Phase 0 gate already used for Coinbase and FRED.
