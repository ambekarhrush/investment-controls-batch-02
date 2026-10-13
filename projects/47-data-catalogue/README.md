# Data catalogue and vendor review workflow

A research team needs to find data, identify its owner and permitted use, and understand downstream impact before a vendor field changes. This module combines dataset metadata, field lineage and mandatory review checks.

## Demonstrated result

Three fictional datasets pass their required checks. `DS_ALT` is **blocked** because its licence review fails; a warning alone does not block approval. A source-field change for Vendor Alpha traces to the risk engine and liquidity monitor.

```bash
uv run investment-controls catalogue
```

Open [the catalogue](outputs/demo/catalogue.html), [review decisions](outputs/demo/review_decisions.csv), or [change impact](outputs/demo/vendor_change_impact.csv). A production service would add authentication, steward approvals and a metadata database.
