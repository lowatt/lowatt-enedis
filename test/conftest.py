from typing import Any

import pytest


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--regen-test-data",
        action="store_true",
        default=False,
        help="Re-generate test data from actual results",
    )


@pytest.fixture
def regen_test_data(request: Any) -> bool:
    value = request.config.getoption("--regen-test-data")
    assert isinstance(value, bool)
    return value
