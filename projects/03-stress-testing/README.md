# Historical and hypothetical stress testing

This engine applies coherent cross-asset shocks and preserves position-level attribution. Equities and commodities use factor sensitivities, bonds use duration and spread duration, and the SPX put receives full Black-Scholes repricing.

![Stress losses](outputs/demo/stress-results.png)

## Demonstrated result

Two versioned scenarios run on a synthetic £1.31m portfolio. The output distinguishes a historical replay-shaped scenario from a hypothetical inflation scenario and shows exactly which positions create each result.

```bash
uv run investment-controls stress
```

Inspect [position attribution](outputs/demo/position_attribution.csv), [scenario totals](outputs/demo/scenario_totals.csv), and [scenario definitions](data/fixtures/scenarios.json). The historical label is illustrative rather than an exact market reconstruction; the engine omits correlation dynamics, liquidity and path dependence.
