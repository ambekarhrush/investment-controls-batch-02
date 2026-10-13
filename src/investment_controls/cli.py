"""Command-line entry point for Batch 02."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from typing import Any

from investment_controls import (
    attribution,
    catalogue,
    fixtures,
    mandate_monitoring,
    payment_reconciliation,
    point_in_time,
    reporting,
    stress_testing,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the investment controls portfolio batch")
    parser.add_argument(
        "command",
        choices=[
            "fixtures",
            "point-in-time",
            "catalogue",
            "payments",
            "stress",
            "attribution",
            "mandates",
            "report",
            "all",
        ],
    )
    command = parser.parse_args().command
    runners: dict[str, Callable[[], Any]] = {
        "fixtures": fixtures.generate_all,
        "point-in-time": point_in_time.run,
        "catalogue": catalogue.run,
        "payments": payment_reconciliation.run,
        "stress": stress_testing.run,
        "attribution": attribution.run,
        "mandates": mandate_monitoring.run,
        "report": reporting.run,
    }
    if command == "all":
        fixtures.generate_all()
        result = {
            name: runner() for name, runner in runners.items() if name not in {"fixtures", "report"}
        }
        result["report"] = reporting.run()
    else:
        result = runners[command]()
    if result is not None:
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
