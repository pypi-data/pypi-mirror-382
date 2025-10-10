import pytest

from pylemetry import registry
from pylemetry.decorators import count
from pylemetry.meters import Counter, MeterType


@count()
def mock_function() -> str:
    return "A function decorated with the count decorator"


def test_count_decorator_creates_counter_in_registry() -> None:
    counter_name = "mock_function"

    assert registry.get_counter(counter_name) is None

    mock_function()

    counter = registry.get_counter(counter_name)

    assert isinstance(counter, Counter)
    assert counter.get_value() == 1


@pytest.mark.parametrize("call_count", [1, 2, 3, 10, 20, 30, 100, 200, 300])
def test_count_decorator_updates_existing_counter(call_count: int) -> None:
    counter_name = "mock_function"

    assert registry.get_counter(counter_name) is None

    for _ in range(call_count):
        mock_function()

    counter = registry.get_counter(counter_name)

    assert isinstance(counter, Counter)
    assert counter.get_value() == call_count


def test_count_decorator_with_name() -> None:
    @count(name="test_count_meter")
    def mock() -> None:
        print("Mock method")

    mock()

    assert "test_count_meter" in registry.METERS[MeterType.COUNTER]
