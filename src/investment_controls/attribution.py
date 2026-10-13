"""Project 04: Brinson-Fachler performance attribution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from investment_controls.common import fingerprint, project_path, write_json

PROJECT = "04-brinson-attribution"


def calculate(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    data = frame.copy()
    benchmark_return = float((data.benchmark_weight * data.benchmark_return).sum())
    portfolio_return = float((data.portfolio_weight * data.portfolio_return).sum())
    data["allocation"] = (data.portfolio_weight - data.benchmark_weight) * (
        data.benchmark_return - benchmark_return
    )
    data["selection"] = data.benchmark_weight * (data.portfolio_return - data.benchmark_return)
    data["interaction"] = (data.portfolio_weight - data.benchmark_weight) * (
        data.portfolio_return - data.benchmark_return
    )
    data["total_effect"] = data[["allocation", "selection", "interaction"]].sum(axis=1)
    metrics = {
        "portfolio_return": portfolio_return,
        "benchmark_return": benchmark_return,
        "active_return": portfolio_return - benchmark_return,
        "attributed_active_return": float(data.total_effect.sum()),
    }
    return data, metrics


def run(input_dir: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    input_dir = input_dir or project_path(PROJECT, "data", "fixtures")
    output_dir = output_dir or project_path(PROJECT, "outputs", "demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    input_path = input_dir / "attribution.csv"
    frame = pd.read_csv(input_path)
    detail, metrics = calculate(frame)
    detail.to_csv(output_dir / "sector_attribution.csv", index=False)
    effects = detail[["allocation", "selection", "interaction"]].sum()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(
        effects.index.str.title(), effects.values * 10000, color=["#26547c", "#2a9d8f", "#e9a23b"]
    )
    ax.axhline(0, color="#243746", linewidth=0.8)
    ax.set_ylabel("Contribution (basis points)")
    ax.set_title("Active return decomposition")
    fig.tight_layout()
    fig.savefig(output_dir / "attribution-effects.png", dpi=180)
    plt.close(fig)
    summary: dict[str, Any] = {
        "snapshot_id": "brinson-demo-2026-09-30",
        "as_of_date": "2026-09-30",
        **metrics,
        "allocation_effect": float(effects.allocation),
        "selection_effect": float(effects.selection),
        "interaction_effect": float(effects.interaction),
        "reconciliation_error": float(
            metrics["active_return"] - metrics["attributed_active_return"]
        ),
        "input_fingerprint": fingerprint([input_path]),
    }
    write_json(output_dir / "summary.json", summary)
    return summary
