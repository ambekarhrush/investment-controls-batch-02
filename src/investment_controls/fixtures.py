"""Deterministic fixtures for all Batch 02 projects."""

from __future__ import annotations

import json

import pandas as pd

from investment_controls.common import project_path, write_csv


def point_in_time() -> None:
    folder = project_path("45-point-in-time-dataset", "data", "fixtures")
    releases = pd.DataFrame(
        [
            ["GDP_US_Q1", "2026-03-31", 2.0, "2026-04-30T12:30:00Z", "2026-04-30T12:32:00Z", 1],
            ["GDP_US_Q1", "2026-03-31", 1.2, "2026-05-28T12:30:00Z", "2026-05-28T12:33:00Z", 2],
            ["CPI_US_APR", "2026-04-30", 3.1, "2026-05-12T12:30:00Z", "2026-05-12T12:31:00Z", 1],
            ["CPI_US_APR", "2026-04-30", 3.0, "2026-06-10T12:30:00Z", "2026-06-10T12:31:00Z", 2],
        ],
        columns=[
            "series_id",
            "observation_date",
            "value",
            "publication_timestamp",
            "ingestion_timestamp",
            "vintage",
        ],
    )
    decisions = pd.DataFrame(
        [
            ["D1", "2026-05-15T16:00:00Z"],
            ["D2", "2026-06-15T16:00:00Z"],
        ],
        columns=["decision_id", "decision_timestamp"],
    )
    write_csv(releases, folder / "releases.csv")
    write_csv(decisions, folder / "decisions.csv")


def catalogue() -> None:
    folder = project_path("47-data-catalogue", "data", "fixtures")
    datasets = pd.DataFrame(
        [
            [
                "DS_MARKET",
                "Daily market prices",
                "Market Data",
                "approved",
                "internal-research",
                "Vendor Alpha",
                "2026-09-30",
            ],
            [
                "DS_POS",
                "Portfolio positions",
                "Operations",
                "approved",
                "restricted",
                "Internal",
                "2026-09-30",
            ],
            [
                "DS_MACRO",
                "Point-in-time macro vintages",
                "Research Data",
                "approved",
                "public-derived",
                "Vendor Beta",
                "2026-09-30",
            ],
            [
                "DS_ALT",
                "Alternative web signals",
                "Research Data",
                "pending",
                "evaluation-only",
                "Vendor Gamma",
                "2026-09-25",
            ],
        ],
        columns=["dataset_id", "name", "owner", "review_state", "usage", "vendor", "reviewed_at"],
    )
    fields = pd.DataFrame(
        [
            ["DS_MARKET", "close", "float", "daily_close", "risk_engine"],
            ["DS_MARKET", "volume", "integer", "daily_volume", "liquidity_monitor"],
            ["DS_POS", "market_value", "float", "position_value", "risk_engine"],
            ["DS_MACRO", "value", "float", "released_value", "regime_research"],
            ["DS_ALT", "signal", "float", "vendor_score", "factor_research"],
        ],
        columns=["dataset_id", "field", "data_type", "source_field", "consumer"],
    )
    checks = pd.DataFrame(
        [
            ["DS_MARKET", "freshness", "pass"],
            ["DS_MARKET", "completeness", "pass"],
            ["DS_POS", "access_review", "pass"],
            ["DS_MACRO", "vintage_coverage", "pass"],
            ["DS_ALT", "license_review", "fail"],
            ["DS_ALT", "history_coverage", "warning"],
        ],
        columns=["dataset_id", "check_name", "status"],
    )
    for name, frame in [("datasets.csv", datasets), ("fields.csv", fields), ("checks.csv", checks)]:
        write_csv(frame, folder / name)


def payments() -> None:
    folder = project_path("48-payment-reconciliation", "data", "fixtures")
    events = pd.DataFrame(
        [
            ["E1", "P1", "settlement", 100.0, "2026-09-30T09:00:00Z"],
            ["E2", "P1", "fee", 2.0, "2026-09-30T09:01:00Z"],
            ["E3", "P2", "settlement", 50.0, "2026-09-30T10:00:00Z"],
            ["E3", "P2", "settlement", 50.0, "2026-09-30T10:00:00Z"],
            ["E4", "P2", "reversal", 50.0, "2026-09-30T11:00:00Z"],
        ],
        columns=["event_id", "payment_id", "event_type", "amount", "event_timestamp"],
    )
    statement = pd.DataFrame(
        [
            ["S1", "P1", 100.0],
            ["S2", "P1", -2.0],
            ["S3", "P2", 50.0],
            ["S4", "P2", -50.0],
            ["S5", "P3", 75.0],
        ],
        columns=["statement_id", "payment_id", "amount"],
    )
    write_csv(events, folder / "events.csv")
    write_csv(statement, folder / "statement.csv")


def stress() -> None:
    folder = project_path("03-stress-testing", "data", "fixtures")
    holdings = pd.DataFrame(
        [
            ["US_EQ", "equity", 400000, "equity_us", 1.0, 0, 0, 0],
            ["EU_EQ", "equity", 250000, "equity_eu", 1.0, 0, 0, 0],
            ["UST_10Y", "bond", 300000, "rates_us", 0, 7.5, 55, 0],
            ["IG_CREDIT", "bond", 220000, "credit_ig", 0, 4.0, 4.5, 0],
            ["OIL", "commodity", 130000, "oil", 1.0, 0, 0, 0],
            ["SPX_PUT", "put", 10000, "equity_us", 0, 0, 0, 0.22],
        ],
        columns=[
            "instrument_id",
            "instrument_type",
            "market_value",
            "primary_factor",
            "beta",
            "duration",
            "spread_duration",
            "volatility",
        ],
    )
    scenarios = {
        "historical_replay": {
            "label": "2020-style risk shock replay",
            "type": "historical replay",
            "shocks": {
                "equity_us": -0.20,
                "equity_eu": -0.24,
                "rates_us": -0.0075,
                "credit_ig": 0.015,
                "oil": -0.30,
                "volatility": 0.18,
            },
        },
        "inflation_hypothetical": {
            "label": "Persistent inflation hypothetical",
            "type": "hypothetical",
            "shocks": {
                "equity_us": -0.08,
                "equity_eu": -0.10,
                "rates_us": 0.01,
                "credit_ig": 0.006,
                "oil": 0.15,
                "volatility": 0.08,
            },
        },
    }
    write_csv(holdings, folder / "holdings.csv")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "scenarios.json").write_text(json.dumps(scenarios, indent=2) + "\n")


def attribution() -> None:
    folder = project_path("04-brinson-attribution", "data", "fixtures")
    frame = pd.DataFrame(
        [
            ["Technology", 0.32, 0.28, 0.06, 0.04],
            ["Financials", 0.20, 0.22, 0.01, 0.015],
            ["Healthcare", 0.18, 0.20, 0.025, 0.03],
            ["Industrials", 0.15, 0.12, 0.04, 0.02],
            ["Consumer", 0.15, 0.10, -0.01, 0.005],
            ["Utilities", 0, 0.08, 0, 0.01],
        ],
        columns=[
            "sector",
            "portfolio_weight",
            "benchmark_weight",
            "portfolio_return",
            "benchmark_return",
        ],
    )
    write_csv(frame, folder / "attribution.csv")


def mandate() -> None:
    folder = project_path("06-mandate-monitoring", "data", "fixtures")
    rules = pd.DataFrame(
        [
            ["MAX_SINGLE", "max_single_weight", 0.25, "high"],
            ["MAX_SECTOR", "max_sector_weight", 0.40, "high"],
            ["MIN_LIQUID", "min_liquid_weight", 0.05, "medium"],
            ["MAX_DRAWDOWN", "max_drawdown", 0.10, "high"],
            ["FRESHNESS", "max_age_hours", 24, "critical"],
        ],
        columns=["rule_id", "metric", "limit", "severity"],
    )
    snapshots = pd.DataFrame(
        [
            ["S1", "2026-09-25T18:00:00Z", "2026-09-25T18:10:00Z", 0.22, 0.38, 0.08, 0.02],
            ["S2", "2026-09-26T18:00:00Z", "2026-09-26T18:05:00Z", 0.28, 0.43, 0.06, 0.04],
            ["S3", "2026-09-27T18:00:00Z", "2026-09-27T18:05:00Z", 0.29, 0.44, 0.06, 0.05],
            ["S4", "2026-09-28T18:00:00Z", "2026-09-28T18:05:00Z", 0.23, 0.39, 0.07, 0.06],
            ["S5", "2026-09-29T18:00:00Z", "2026-10-01T00:00:00Z", 0.30, 0.45, 0.04, 0.12],
        ],
        columns=[
            "snapshot_id",
            "as_of",
            "received_at",
            "max_single_weight",
            "max_sector_weight",
            "liquid_weight",
            "drawdown",
        ],
    )
    write_csv(rules, folder / "rules.csv")
    write_csv(snapshots, folder / "snapshots.csv")


def generate_all() -> None:
    point_in_time()
    catalogue()
    payments()
    stress()
    attribution()
    mandate()


if __name__ == "__main__":
    generate_all()
