"""Project 03: transparent historical and hypothetical stress testing."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm

from investment_controls.common import fingerprint, project_path, write_json

PROJECT = "03-stress-testing"


def _put_price(spot: float, strike: float, maturity: float, rate: float, vol: float) -> float:
    d1 = (math.log(spot / strike) + (rate + vol**2 / 2) * maturity) / (vol * math.sqrt(maturity))
    d2 = d1 - vol * math.sqrt(maturity)
    return strike * math.exp(-rate * maturity) * norm.cdf(-d2) - spot * norm.cdf(-d1)


def run(input_dir: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    input_dir = input_dir or project_path(PROJECT, "data", "fixtures")
    output_dir = output_dir or project_path(PROJECT, "outputs", "demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    holdings_path, scenarios_path = input_dir / "holdings.csv", input_dir / "scenarios.json"
    holdings = pd.read_csv(holdings_path)
    scenarios = json.loads(scenarios_path.read_text())
    base_put = _put_price(100, 90, 0.5, 0.03, 0.22)
    rows: list[dict[str, Any]] = []
    for scenario_id, scenario in scenarios.items():
        shocks = scenario["shocks"]
        for h in holdings.itertuples(index=False):
            method = "linear factor sensitivity"
            if h.instrument_type == "equity":
                pnl = h.market_value * h.beta * shocks[h.primary_factor]
            elif h.instrument_type == "commodity":
                pnl = h.market_value * shocks[h.primary_factor]
            elif h.instrument_id == "UST_10Y":
                pnl = -h.market_value * h.duration * shocks["rates_us"]
            elif h.instrument_id == "IG_CREDIT":
                pnl = -h.market_value * (
                    h.duration * shocks["rates_us"] + h.spread_duration * shocks["credit_ig"]
                )
            else:
                shocked = _put_price(
                    100 * (1 + shocks["equity_us"]), 90, 0.5, 0.03, 0.22 + shocks["volatility"]
                )
                pnl = h.market_value * (shocked / base_put - 1)
                method = "Black-Scholes full repricing"
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "scenario_label": scenario["label"],
                    "scenario_type": scenario["type"],
                    "instrument_id": h.instrument_id,
                    "method": method,
                    "pnl": pnl,
                }
            )
    detail = pd.DataFrame(rows)
    totals = detail.groupby(
        ["scenario_id", "scenario_label", "scenario_type"], as_index=False
    ).pnl.sum()
    detail.to_csv(output_dir / "position_attribution.csv", index=False)
    totals.to_csv(output_dir / "scenario_totals.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#b14c3c" if x < 0 else "#237a6b" for x in totals.pnl]
    ax.bar(totals.scenario_label, totals.pnl / 1000, color=colors)
    ax.axhline(0, color="#243746", linewidth=0.8)
    ax.set_ylabel("Portfolio P&L (£000)")
    ax.set_title("Stress loss by scenario")
    ax.tick_params(axis="x", rotation=8)
    fig.tight_layout()
    fig.savefig(output_dir / "stress-results.png", dpi=180)
    plt.close(fig)
    summary = {
        "snapshot_id": "stress-demo-v1",
        "as_of_date": "2026-09-30",
        "portfolio_market_value": float(holdings.market_value.sum()),
        "scenario_count": len(scenarios),
        "worst_scenario": totals.loc[totals.pnl.idxmin(), "scenario_label"],
        "worst_pnl": float(totals.pnl.min()),
        "nonlinear_positions": int(holdings.instrument_type.eq("put").sum()),
        "input_fingerprint": fingerprint([holdings_path, scenarios_path]),
    }
    write_json(output_dir / "summary.json", summary)
    return summary
