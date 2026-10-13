"""Build the cross-project evidence report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from investment_controls.common import ROOT, write_json

PROJECTS = [
    (
        "45-point-in-time-dataset",
        "Point-in-time research data",
        "naive_leaks",
        "future values caught",
    ),
    ("47-data-catalogue", "Data catalogue", "blocked", "dataset blocked"),
    ("48-payment-reconciliation", "Payment reconciliation", "reconciliation_breaks", "break found"),
    ("03-stress-testing", "Stress testing", "scenario_count", "scenarios run"),
    (
        "04-brinson-attribution",
        "Brinson attribution",
        "reconciliation_error",
        "reconciliation error",
    ),
    ("06-mandate-monitoring", "Mandate monitoring", "new_breaches", "new breaches"),
]


def run(output_dir: Path | None = None) -> dict[str, Any]:
    output_dir = output_dir or ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    cards = []
    for slug, title, field, label in PROJECTS:
        summary_path = ROOT / "projects" / slug / "outputs" / "demo" / "summary.json"
        summary = json.loads(summary_path.read_text())
        records.append({"project": slug, "summary": str(summary_path.relative_to(ROOT)), **summary})
        value = summary[field]
        shown = f"{value:.2e}" if isinstance(value, float) and abs(value) < 0.001 else str(value)
        cards.append(
            f"<article><p class='eyebrow'>{slug[:2]}</p><h2>{title}</h2><p class='metric'>{shown}</p><p>{label}</p><a href='../projects/{slug}/README.md'>Read project brief →</a></article>"
        )
    manifest = {"batch": "02", "project_count": len(records), "projects": records}
    write_json(output_dir / "manifest.json", manifest)
    html = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Investment Controls · Batch 02</title><style>
    :root{{--ink:#152c3d;--paper:#f4f1e9;--accent:#bb5a3c;--muted:#61727d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui}}header{{padding:72px max(6vw,24px);background:#142b3a;color:white}}header p{{max-width:720px;color:#c7d5dc}}h1{{font:700 clamp(42px,7vw,78px)/1.02 Georgia,serif;max-width:900px;margin:.2em 0}}main{{padding:48px max(6vw,24px)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;max-width:1200px}}article{{background:white;padding:28px;border-top:4px solid var(--accent);box-shadow:0 8px 24px #18334412}}h2{{font:600 21px Georgia,serif}}.eyebrow{{letter-spacing:.14em;color:var(--accent);font-weight:700}}.metric{{font:700 36px Georgia,serif;margin:.35em 0 0}}a{{color:#174f6c;font-weight:650}}footer{{padding:20px max(6vw,24px) 50px;color:var(--muted)}}</style></head><body><header><p>INVESTMENT RESEARCH &amp; CONTROLS · BATCH 02</p><h1>Six small systems. One traceable evidence trail.</h1><p>Deterministic demonstrations of information timing, data governance, cash controls, portfolio risk, performance explanation and mandate oversight.</p></header><main><div class='grid'>{"".join(cards)}</div></main><footer>Synthetic fixtures · reproducible locally · generated from tested code</footer></body></html>"""
    (output_dir / "batch-report.html").write_text(html)
    return manifest
