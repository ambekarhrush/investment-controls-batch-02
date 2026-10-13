from __future__ import annotations

import pytest

from investment_controls.fixtures import generate_all


@pytest.fixture(scope="session", autouse=True)
def generated_fixtures() -> None:
    generate_all()
