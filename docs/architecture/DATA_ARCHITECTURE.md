# DATA ARCHITECTURE

## Layers

### RAW
Original provider payloads, timestamps, source identity, fetch metadata, hashes and schema/version metadata. RAW records are append-only.

### NORMALIZED
Canonical observations independent of vendor naming: asset, venue/source, metric, timestamp, value, units, provenance and quality flags.

### DERIVED
Versioned features, aggregates, regime labels, anomaly scores and other reproducible calculations derived only from known inputs.

## Point-in-time snapshots

A `data_snapshot` identifies the exact set/version frontier of observations available to a forecast. Forecast evaluation must use the snapshot lineage, not today's revised history.

## Data quality

Every source/metric should eventually expose freshness, missingness, duplication, late-arrival and revision indicators. UNKNOWN or stale data must remain visible rather than being silently imputed unless the feature definition explicitly specifies imputation.

## Phase 0 source families

Design schemas for: market price/volume, derivatives (OI/funding/liquidations/taker flow), macro, basic on-chain, stablecoin metrics, and structured news/events.

Do not start broad altcoin or high-frequency order-book collection in Phase 0.
