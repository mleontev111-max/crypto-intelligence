# BTC MVP

## Scope

Phase 1 begins with BTC only. Initial working instrument may be BTC/USDT for market data, while macro/on-chain metrics remain asset-level BTC context.

## Planned horizons

- 4h
- 24h
- 7d

## Initial signal families

### Market
Returns, volume, volatility/ATR, relative volume and selected liquidity/market-structure metrics.

### Derivatives
Open interest, OI change, funding, funding percentile, long/short liquidations, taker buy/sell measures where source quality permits.

### On-chain / stablecoins
Exchange inflow/outflow/netflow, exchange reserves, selected MVRV/SOPR-style metrics, and stablecoin liquidity/reserve metrics subject to source availability and licensing.

### Macro
DXY, Nasdaq/S&P risk proxies, VIX, US 2Y/10Y yields, and scheduled macro events with expected/actual/surprise where reliable point-in-time data is available.

### News/events
Structured event records: type, entities/assets, timestamp, source/credibility, novelty/relevance and evidence. Do not assign fake causal percentages.

## Excluded from initial MVP

- broad altcoin universe;
- autonomous trading;
- high-frequency/HFT order-book strategies;
- full options analytics;
- social-media firehose;
- reinforcement learning;
- self-modifying production models.

## First success criterion

The first success is not profitable trading. It is a trustworthy, observable BTC data pipeline with reproducible point-in-time snapshots and enough quality metadata to support later honest forecasts.
