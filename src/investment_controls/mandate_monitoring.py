"""Project 06: stateful investment mandate monitoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from investment_controls.common import fingerprint, project_path, write_json

PROJECT = "06-mandate-monitoring"


def _violates(metric: str, value: float, limit: float) -> bool:
    return value < limit if metric.startswith("min_") else value > limit


def _snapshot_field(metric: str) -> str:
    return {"min_liquid_weight": "liquid_weight", "max_drawdown": "drawdown"}.get(metric, metric)


def run(input_dir: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    input_dir = input_dir or project_path(PROJECT, "data", "fixtures")
    output_dir = output_dir or project_path(PROJECT, "outputs", "demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    rules_path, snapshots_path = input_dir / "rules.csv", input_dir / "snapshots.csv"
    rules, snapshots = pd.read_csv(rules_path), pd.read_csv(snapshots_path)
    portfolio_rules = rules[rules.rule_id != "FRESHNESS"]
    states: dict[str, str] = {}
    events: list[dict[str, Any]] = []
    for snap in snapshots.itertuples(index=False):
        age = (pd.Timestamp(snap.received_at) - pd.Timestamp(snap.as_of)).total_seconds() / 3600
        if age > float(rules.loc[rules.rule_id == "FRESHNESS", "limit"].iloc[0]):
            events.append(
                {
                    "snapshot_id": snap.snapshot_id,
                    "rule_id": "FRESHNESS",
                    "event": "stale_data",
                    "value": age,
                    "limit": 24.0,
                    "severity": "critical",
                }
            )
            continue
        for rule in portfolio_rules.itertuples(index=False):
            value = float(getattr(snap, _snapshot_field(rule.metric)))
            breached = _violates(rule.metric, value, float(rule.limit))
            prior = states.get(rule.rule_id, "clear")
            if breached and prior == "clear":
                event, states[rule.rule_id] = "new", "open"
            elif breached and prior == "open":
                event, states[rule.rule_id] = "acknowledged", "acknowledged"
            elif breached:
                continue
            elif not breached and prior in {"open", "acknowledged"}:
                event, states[rule.rule_id] = "resolved", "clear"
            else:
                continue
            events.append(
                {
                    "snapshot_id": snap.snapshot_id,
                    "rule_id": rule.rule_id,
                    "event": event,
                    "value": value,
                    "limit": float(rule.limit),
                    "severity": rule.severity,
                }
            )
    history = pd.DataFrame(events)
    history.to_csv(output_dir / "event_history.csv", index=False)
    queue = pd.DataFrame(
        [{"rule_id": key, "state": value} for key, value in states.items() if value != "clear"],
        columns=["rule_id", "state"],
    )
    queue.to_csv(output_dir / "current_queue.csv", index=False)
    payload = {
        "as_of_snapshot": snapshots.iloc[-1].snapshot_id,
        "events": history.to_dict(orient="records"),
    }
    write_json(output_dir / "webhook_payload.json", payload)
    summary = {
        "snapshot_id": "mandate-replay-v1",
        "as_of_date": "2026-10-01",
        "snapshots_replayed": len(snapshots),
        "new_breaches": int((history.event == "new").sum()),
        "acknowledged_breaches": int((history.event == "acknowledged").sum()),
        "resolved_breaches": int((history.event == "resolved").sum()),
        "stale_snapshots": int((history.event == "stale_data").sum()),
        "open_breaches": len(queue),
        "input_fingerprint": fingerprint([rules_path, snapshots_path]),
    }
    write_json(output_dir / "summary.json", summary)
    return summary
