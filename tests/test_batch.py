from __future__ import annotations

import json

import pandas as pd
import pytest

from investment_controls import (
    attribution,
    catalogue,
    mandate_monitoring,
    payment_reconciliation,
    point_in_time,
    reporting,
    stress_testing,
)
from investment_controls.common import ROOT


def test_point_in_time_blocks_future_revisions() -> None:
    result = point_in_time.run()
    rows = pd.read_csv(ROOT / "projects/45-point-in-time-dataset/outputs/demo/asof_comparison.csv")
    assert result["naive_leaks"] == 2
    assert set(rows.query("decision_id == 'D1'").asof_vintage) == {1}


def test_catalogue_blocks_failed_review_and_maps_lineage() -> None:
    result = catalogue.run()
    decisions = pd.read_csv(ROOT / "projects/47-data-catalogue/outputs/demo/review_decisions.csv")
    assert decisions.set_index("dataset_id").loc["DS_ALT", "derived_state"] == "blocked"
    assert result["vendor_change_consumers"] == ["liquidity_monitor", "risk_engine"]


def test_payment_ledger_balances_and_reconciliation_finds_break() -> None:
    result = payment_reconciliation.run()
    ledger = pd.read_csv(ROOT / "projects/48-payment-reconciliation/outputs/demo/ledger.csv")
    by_event = ledger.groupby("event_id")[["debit", "credit"]].sum()
    assert (by_event.debit == by_event.credit).all()
    assert result["duplicate_events_ignored"] == 1
    assert result["reconciliation_breaks"] == 1


def test_stress_detail_reconciles_to_totals() -> None:
    stress_testing.run()
    base = ROOT / "projects/03-stress-testing/outputs/demo"
    detail, totals = (
        pd.read_csv(base / "position_attribution.csv"),
        pd.read_csv(base / "scenario_totals.csv"),
    )
    calculated = detail.groupby("scenario_id").pnl.sum()
    reported = totals.set_index("scenario_id").pnl
    pd.testing.assert_series_equal(
        calculated.sort_index(), reported.sort_index(), check_names=False
    )
    assert (
        detail.query("instrument_id == 'SPX_PUT'").method == "Black-Scholes full repricing"
    ).all()


def test_brinson_reconciles_exactly() -> None:
    result = attribution.run()
    assert result["reconciliation_error"] == pytest.approx(0, abs=1e-12)
    assert result["active_return"] == pytest.approx(result["attributed_active_return"])


def test_mandate_state_transitions_and_stale_suppression() -> None:
    result = mandate_monitoring.run()
    events = pd.read_csv(ROOT / "projects/06-mandate-monitoring/outputs/demo/event_history.csv")
    assert result == {
        **result,
        "new_breaches": 2,
        "acknowledged_breaches": 2,
        "resolved_breaches": 2,
        "stale_snapshots": 1,
    }
    assert len(events.query("snapshot_id == 'S5'")) == 1
    assert events.query("snapshot_id == 'S5'").iloc[0].event == "stale_data"


def test_batch_report_has_six_provenance_records() -> None:
    for runner in [
        point_in_time.run,
        catalogue.run,
        payment_reconciliation.run,
        stress_testing.run,
        attribution.run,
        mandate_monitoring.run,
    ]:
        runner()
    manifest = reporting.run()
    assert manifest["project_count"] == 6
    persisted = json.loads((ROOT / "outputs/manifest.json").read_text())
    assert all("input_fingerprint" in project for project in persisted["projects"])
