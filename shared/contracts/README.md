# Shared contracts

Every project writes a `summary.json` with a snapshot ID, as-of date, measured results and a SHA-256 input fingerprint. The batch report reads only these public output contracts. This keeps each project replaceable while preserving a stable integration boundary.
