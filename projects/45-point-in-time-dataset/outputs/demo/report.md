# Point-in-time research dataset

A latest-value join uses facts that had not been published at the decision time.

| Decision | Series | Available value | Naive latest | Difference |
| --- | --- | ---: | ---: | ---: |
| D1 | CPI_US_APR | 3.10 | 3.00 | -0.10 |
| D1 | GDP_US_Q1 | 2.00 | 1.20 | -0.80 |

**2 leaked joins** are excluded by checking both publication and ingestion timestamps.

The fixture is synthetic. It demonstrates information timing rather than macro forecast performance.
