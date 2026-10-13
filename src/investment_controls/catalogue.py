"""Project 47: searchable data catalogue and vendor review workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from investment_controls.common import fingerprint, project_path, write_json

PROJECT = "47-data-catalogue"


def search(datasets: pd.DataFrame, fields: pd.DataFrame, term: str) -> pd.DataFrame:
    text = datasets.name.str.cat(datasets[["owner", "usage", "vendor"]].astype(str), sep=" ")
    ids = set(datasets.loc[text.str.contains(term, case=False, regex=False), "dataset_id"])
    ids.update(
        fields.loc[
            fields.astype(str)
            .apply(lambda col: col.str.contains(term, case=False, regex=False))
            .any(axis=1),
            "dataset_id",
        ]
    )
    return datasets[datasets.dataset_id.isin(ids)]


def run(input_dir: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    input_dir = input_dir or project_path(PROJECT, "data", "fixtures")
    output_dir = output_dir or project_path(PROJECT, "outputs", "demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [input_dir / name for name in ["datasets.csv", "fields.csv", "checks.csv"]]
    datasets, fields, checks = (pd.read_csv(path) for path in paths)
    failed = checks[checks.status == "fail"].groupby("dataset_id").size()
    workflow = datasets[["dataset_id", "review_state"]].copy()
    workflow["derived_state"] = workflow.dataset_id.map(
        lambda x: "blocked" if failed.get(x, 0) else "approved"
    )
    workflow["decision_reason"] = workflow.dataset_id.map(
        lambda x: "Failed mandatory review check" if failed.get(x, 0) else "Mandatory checks passed"
    )
    workflow.to_csv(output_dir / "review_decisions.csv", index=False)
    risk_search = search(datasets, fields, "risk")
    risk_search.to_csv(output_dir / "search_risk.csv", index=False)
    alpha_fields = fields[fields.dataset_id == "DS_MARKET"].copy()
    affected = alpha_fields[["field", "consumer"]].assign(
        change="Vendor Alpha renames close to px_close"
    )
    affected.to_csv(output_dir / "vendor_change_impact.csv", index=False)
    summary = {
        "snapshot_id": "catalogue-2026-09-30",
        "as_of_date": "2026-09-30",
        "datasets": len(datasets),
        "approved": int((workflow.derived_state == "approved").sum()),
        "blocked": int((workflow.derived_state == "blocked").sum()),
        "risk_search_results": len(risk_search),
        "vendor_change_consumers": sorted(affected.consumer.unique().tolist()),
        "input_fingerprint": fingerprint(paths),
    }
    write_json(output_dir / "summary.json", summary)
    cards = "".join(
        f"<tr><td>{r.dataset_id}</td><td>{r.name}</td><td>{r.owner}</td><td>{workflow.loc[workflow.dataset_id == r.dataset_id, 'derived_state'].iloc[0]}</td><td>{r.usage}</td></tr>"
        for _, r in datasets.iterrows()
    )
    (output_dir / "catalogue.html").write_text(
        f"""<!doctype html><meta charset='utf-8'><title>Data catalogue</title><style>body{{font:15px/1.5 system-ui;max-width:1050px;margin:40px auto;color:#17324d}}h1{{font-size:38px}}table{{width:100%;border-collapse:collapse}}td,th{{padding:11px;border-bottom:1px solid #dce4eb;text-align:left}}th{{background:#edf3f7}}.notice{{border-left:4px solid #b3682e;background:#fff7eb;padding:14px}}</style><h1>Data catalogue and vendor review</h1><p>Searchable fictional catalogue · owner, usage, lineage and review state</p><div class='notice'>DS_ALT is blocked because its mandatory license review failed. A warning alone would not block approval.</div><table><tr><th>ID</th><th>Dataset</th><th>Owner</th><th>Decision</th><th>Usage</th></tr>{cards}</table><h2>Change impact</h2><p>A source-field change to Vendor Alpha reaches: {", ".join(summary["vendor_change_consumers"])}. The field-to-consumer export makes the dependency reviewable.</p>"""
    )
    return summary
