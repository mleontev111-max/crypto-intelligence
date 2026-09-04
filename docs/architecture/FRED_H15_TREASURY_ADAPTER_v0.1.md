# FRED H.15 Treasury Adapter Contract v0.1

**Status:** Canonical adapter contract; live ingestion disabled.  
**Source ID:** `macro.fred.h15.dgs2_dgs10`  
**Series:** `DGS2`, `DGS10`  
**Mode:** read-only internal research.

## Access

FRED API v1 `fred/series/observations` over HTTPS GET.

Runtime API key is required by FRED and must be supplied from secret/environment configuration. It must never be committed, logged, stored in RAW payload metadata, or exposed to client code.

## Approved series

- `DGS2` — Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity, daily, percent, not seasonally adjusted.
- `DGS10` — Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, daily, percent, not seasonally adjusted.

FRED identifies both series as Board of Governors H.15 data and tags them `Public Domain: Citation Requested`.

## Point-in-time / revision contract

FRED exposes real-time periods and vintage controls. Adapter requests must explicitly carry `realtime_start` and `realtime_end` when reconstructing historical vintages; latest-history pulls must never be treated as proof that revised values were known earlier.

For every response store:

- series ID;
- request real-time parameters;
- response observation date;
- FRED real-time start/end fields when present;
- `observed_at` and `ingested_at` from our collector;
- `available_at` no earlier than collector first-seen time unless a separately verified publication timestamp is available;
- content hash and raw response reference.

Revisions append new RAW evidence; prior values are never overwritten.

## Missing values

FRED may represent unavailable observations with `.`. Missing values must remain explicit and must not be silently interpolated.

## Terms boundary

FRED API Terms apply and require compliance with source-series rights and attribution requirements. This approval is limited to `DGS2` and `DGS10`, whose current FRED metadata identifies them as public-domain data with citation requested. It is not blanket approval for all FRED series.

If the product later exposes these values publicly, required FRED/source attribution and the FRED API notice must be reviewed again for the exact UI/use.

## Write-free adapter test

Before any database ingestion, tests must prove:

1. only `DGS2`/`DGS10` are accepted;
2. API key is runtime-only and not embedded in persisted metadata;
3. request builder supports explicit real-time/vintage boundaries;
4. `.` remains missing;
5. revised/latest pulls cannot backdate `available_at`;
6. no DB writes or trading functionality exist.