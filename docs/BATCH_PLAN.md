# Batch 02 design

The batch follows an investment process from data to oversight:

1. Reconstruct the information actually available at a decision timestamp.
2. Catalogue data ownership, permitted use, quality gates and downstream lineage.
3. Process payment events once and reconcile the balanced ledger to an external statement.
4. Apply versioned market shocks, including full repricing for a nonlinear option.
5. Explain active return through allocation, selection and interaction.
6. Track mandate breaches through new, acknowledged and resolved states while suppressing stale data.

Each module owns its fixtures and demo outputs. The shared batch report consumes their summary contracts, which avoids coupling analytical implementation details across projects.
