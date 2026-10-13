# Point-in-time research dataset builder

Investment research must use the value that was available at the decision time, not the value a database shows today. This module stores publication and ingestion timestamps in DuckDB and performs an as-of join across both clocks.

## Demonstrated result

At the 15 May decision, GDP and CPI each had only their first vintage available. A naive latest-value join selects later revisions for both: **2 leaked observations**. The guarded query excludes them.

```bash
uv run investment-controls point-in-time
```

Inspect [the comparison](outputs/demo/asof_comparison.csv), [readable report](outputs/demo/report.md), and [summary contract](outputs/demo/summary.json). The fixture is synthetic and tests timing correctness; it does not measure forecast skill.
