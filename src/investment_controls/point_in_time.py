"""Project 45: bitemporal point-in-time dataset construction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from investment_controls.common import fingerprint, project_path, write_json

PROJECT = "45-point-in-time-dataset"


def run(input_dir: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    input_dir = input_dir or project_path(PROJECT, "data", "fixtures")
    output_dir = output_dir or project_path(PROJECT, "outputs", "demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    releases_path, decisions_path = input_dir / "releases.csv", input_dir / "decisions.csv"
    releases, decisions = pd.read_csv(releases_path), pd.read_csv(decisions_path)
    database = output_dir / "vintages.duckdb"
    database.unlink(missing_ok=True)
    with duckdb.connect(str(database)) as con:
        con.register("release_frame", releases)
        con.register("decision_frame", decisions)
        con.execute("create table releases as select * from release_frame")
        con.execute("create table decisions as select * from decision_frame")
        dated = con.execute("""
            select d.decision_id, d.decision_timestamp, s.series_id, r.value as asof_value,
                   r.vintage as asof_vintage, r.publication_timestamp
            from decisions d cross join (select distinct series_id from releases) s
            join lateral (
              select * from releases r
              where r.series_id=s.series_id
                and cast(r.publication_timestamp as timestamp) <= cast(d.decision_timestamp as timestamp)
                and cast(r.ingestion_timestamp as timestamp) <= cast(d.decision_timestamp as timestamp)
              order by cast(r.publication_timestamp as timestamp) desc, vintage desc limit 1
            ) r on true order by d.decision_id, s.series_id
        """).df()
    latest = releases.sort_values(["series_id", "vintage"]).groupby("series_id").tail(1)
    latest = latest[["series_id", "value", "vintage", "publication_timestamp"]].rename(
        columns={
            "value": "value_naive",
            "vintage": "vintage_naive",
            "publication_timestamp": "publication_timestamp_naive",
        }
    )
    comparison = dated.merge(latest, on="series_id")
    comparison["leakage"] = comparison.publication_timestamp_naive > comparison.decision_timestamp
    comparison["value_difference"] = comparison.value_naive - comparison.asof_value
    comparison.to_csv(output_dir / "asof_comparison.csv", index=False)
    summary = {
        "snapshot_id": "point-in-time-demo-v1",
        "as_of_date": "2026-06-15",
        "decision_queries": len(decisions),
        "series": releases.series_id.nunique(),
        "joined_rows": len(comparison),
        "naive_leaks": int(comparison.leakage.sum()),
        "input_fingerprint": fingerprint([releases_path, decisions_path]),
    }
    write_json(output_dir / "summary.json", summary)
    leaked = comparison[comparison.leakage]
    lines = [
        "# Point-in-time research dataset",
        "",
        "A latest-value join uses facts that had not been published at the decision time.",
        "",
        "| Decision | Series | Available value | Naive latest | Difference |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for _, row in leaked.iterrows():
        lines.append(
            f"| {row.decision_id} | {row.series_id} | {row.asof_value:.2f} | {row.value_naive:.2f} | {row.value_difference:+.2f} |"
        )
    lines.extend(
        [
            "",
            f"**{len(leaked)} leaked joins** are excluded by checking both publication and ingestion timestamps.",
            "",
            "The fixture is synthetic. It demonstrates information timing rather than macro forecast performance.",
        ]
    )
    (output_dir / "report.md").write_text("\n".join(lines) + "\n")
    return summary
