import pytest

from pylemetry import registry


@pytest.fixture(autouse=True)
def clear_registry() -> None:
    registry.clear()
