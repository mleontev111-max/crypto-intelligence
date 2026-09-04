# Coinbase BTC-USD Candles Adapter Contract v0.1

**Status:** Canonical adapter contract; implementation not yet enabled.  
**Source ID:** `market.coinbase.exchange.btcusd.candles`  
**Mode:** read-only / internal research only.  
**Live ingestion:** DISABLED.

## Endpoint

Coinbase Exchange REST Market Data:

`GET https://api.exchange.coinbase.com/products/BTC-USD/candles`

Approved request parameters:

- `start`
- `end`
- `granularity`

Adapter must never call account, order, transfer, wallet, or authenticated trading endpoints.

## Granularity

Canonical raw collection candidate for MVP: `3600` seconds (1h).

Reason: 1h can support causal aggregation into 4h/24h/7d research features while avoiding unnecessary 1m volume in Phase 0. Coinbase does not expose native 4h candles in this Exchange endpoint; any 4h bar must be derived by a versioned normalizer from completed 1h bars.

No derived aggregation is authorized to overwrite raw Coinbase candles.

## Response semantics

Each returned bucket maps to:

- bucket start timestamp;
- low;
- high;
- open;
- close;
- volume.

Coinbase documents that historical candle data may be incomplete and that intervals with no ticks may have no published bucket. Missing bars must therefore remain explicit quality state; adapter must not silently synthesize OHLCV rows.

## Point-in-time contract

For every HTTP response, store a RAW record with:

- `source_id = market.coinbase.exchange.btcusd.candles`;
- request URL/parameters in metadata;
- exact response bytes/object reference;
- `observed_at` = collector receive/observation time;
- `ingested_at` = durable persistence time;
- `available_at` = no earlier than the system's first defensible observation time for that returned payload;
- content hash;
- schema version.

The candle's bucket timestamp is `source_event_at`, **not** proof the historical value was known to our system at that old timestamp. Historical backfills therefore retain collection-time `available_at`; they must not be backdated for live point-in-time forecasts.

For later research backtests, historical data may be used only under an explicitly versioned historical-dataset policy that distinguishes vendor event time from system first-seen time.

## Revision policy

`provider_revises_or_unknown`.

No immutable-history guarantee is assumed. Re-fetching a historical range that yields changed content creates new RAW evidence. Never update the original payload in place.

## Pagination / request discipline

- Maximum 300 candles per request.
- Historical endpoint must not be polled frequently.
- Partition requested history into deterministic non-overlapping windows at <=300 1h buckets.
- Retry 429/5xx conservatively with bounded exponential backoff.
- Record HTTP status and response metadata for failed attempts separately from successful RAW market payloads.
- No infinite retry loops.

## Normalization contract

A successful raw candle bucket may normalize into one observation set only after validation:

- numeric OHLCV parses successfully;
- `low <= open/high/close <= high` as applicable;
- volume >= 0;
- timestamp aligns to expected bucket boundary;
- duplicate raw payload lineage is preserved rather than hidden.

Quality flags must represent gaps or suspect data. Silent interpolation is forbidden.

## Terms boundary

Approval is limited to internal/research use permitted by Coinbase Market Data Terms. Do not expose raw Coinbase market data or Coinbase-derived works externally under this Phase 0 approval. Any end-user/public application use requires a fresh terms/legal review and, if necessary, written permission.

## Write-free adapter test required before enabling ingestion

The first implementation must run in a no-database-write fixture/test mode and prove:

1. exact endpoint and `BTC-USD` only;
2. 1h request window <=300 buckets;
3. response parser semantics;
4. timestamp separation (`source_event_at` vs `available_at`);
5. content hashing;
6. gap preservation;
7. no credentials/order methods present;
8. no database writes or live-ingestion flag changes.

Only after that test passes may the project consider a separate checkpoint to permit controlled ingestion.