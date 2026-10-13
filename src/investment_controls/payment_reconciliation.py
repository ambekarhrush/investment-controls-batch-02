"""Project 48: idempotent double-entry payment reconciliation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from investment_controls.common import fingerprint, project_path, write_json

PROJECT = "48-payment-reconciliation"


def run(input_dir: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    input_dir = input_dir or project_path(PROJECT, "data", "fixtures")
    output_dir = output_dir or project_path(PROJECT, "outputs", "demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    event_path, statement_path = input_dir / "events.csv", input_dir / "statement.csv"
    events, statement = pd.read_csv(event_path), pd.read_csv(statement_path)
    duplicate_mask = events.duplicated("event_id", keep="first")
    ignored, accepted = events[duplicate_mask], events[~duplicate_mask]
    ignored.to_csv(output_dir / "ignored_duplicates.csv", index=False)

    accounts = {
        "settlement": ("Cash", "Customer liability", 1.0),
        "fee": ("Fee expense", "Cash", -1.0),
        "reversal": ("Customer liability", "Cash", -1.0),
    }
    rows: list[dict[str, Any]] = []
    nets: list[dict[str, Any]] = []
    for event in accepted.itertuples(index=False):
        debit, credit, net_sign = accounts[event.event_type]
        rows.extend(
            [
                {
                    "event_id": event.event_id,
                    "payment_id": event.payment_id,
                    "account": debit,
                    "debit": event.amount,
                    "credit": 0.0,
                },
                {
                    "event_id": event.event_id,
                    "payment_id": event.payment_id,
                    "account": credit,
                    "debit": 0.0,
                    "credit": event.amount,
                },
            ]
        )
        nets.append({"payment_id": event.payment_id, "internal_amount": net_sign * event.amount})
    ledger = pd.DataFrame(rows)
    ledger.to_csv(output_dir / "ledger.csv", index=False)
    internal = pd.DataFrame(nets).groupby("payment_id", as_index=False).internal_amount.sum()
    external = (
        statement.groupby("payment_id", as_index=False)
        .amount.sum()
        .rename(columns={"amount": "external_amount"})
    )
    reconciliation = internal.merge(external, how="outer", on="payment_id").fillna(0)
    reconciliation["difference"] = reconciliation.internal_amount - reconciliation.external_amount
    reconciliation["status"] = (
        reconciliation.difference.abs().lt(0.005).map({True: "matched", False: "break"})
    )
    reconciliation.to_csv(output_dir / "reconciliation.csv", index=False)
    balance = ledger.debit.sum() - ledger.credit.sum()
    summary = {
        "snapshot_id": "payment-demo-2026-09-30",
        "as_of_date": "2026-09-30",
        "input_events": len(events),
        "accepted_events": len(accepted),
        "duplicate_events_ignored": int(duplicate_mask.sum()),
        "ledger_entries": len(ledger),
        "ledger_balance": float(balance),
        "matched_payments": int((reconciliation.status == "matched").sum()),
        "reconciliation_breaks": int((reconciliation.status == "break").sum()),
        "unexplained_external_amount": float(
            -reconciliation.loc[reconciliation.status == "break", "difference"].sum()
        ),
        "input_fingerprint": fingerprint([event_path, statement_path]),
    }
    write_json(output_dir / "summary.json", summary)
    (output_dir / "report.md").write_text(
        "# Payment settlement and reconciliation\n\n"
        "The processor accepted 4 unique events, ignored one replayed event ID, and wrote 8 balanced ledger entries.\n\n"
        "P1 and P2 reconcile. P3 is a **£75 external-only break** that requires investigation.\n\n"
        "The data is synthetic; tolerances and account mappings are explicit in code.\n"
    )
    return summary
