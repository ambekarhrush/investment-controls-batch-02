# Payment settlement and reconciliation simulator

Payment processing has two separate obligations: each event must post a balanced entry, and the resulting cash must agree with the external statement. This module deduplicates immutable event IDs, writes a double-entry ledger, and reconciles by payment.

## Demonstrated result

Five input rows contain four unique events. The repeated `E3` is ignored, all **8 ledger lines balance**, P1 and P2 match, and external-only P3 creates a **£75 investigation break**.

```bash
uv run investment-controls payments
```

Review the [ledger](outputs/demo/ledger.csv), [reconciliation](outputs/demo/reconciliation.csv), and [control report](outputs/demo/report.md). The account map and zero-tolerance demo policy are explicit; production use would require currency, cut-off and settlement-status rules.
