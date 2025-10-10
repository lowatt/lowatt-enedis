import pytest


@pytest.fixture
def accept(request: pytest.FixtureRequest) -> bool:
    value = request.config.getoption("--accept")
    assert isinstance(value, bool)
    return value
