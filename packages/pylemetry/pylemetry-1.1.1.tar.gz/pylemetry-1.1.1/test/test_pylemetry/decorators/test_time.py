import pytest

from pylemetry import registry
from pylemetry.decorators import time
from pylemetry.meters import Timer, MeterType


@time()
def mock_function() -> str:
    return "A function decorated with the timer decorator"


def test_timer_decorator_creates_counter_in_registry() -> None:
    timer_name = "mock_function"

    assert registry.get_timer(timer_name) is None

    mock_function()

    timer = registry.get_timer(timer_name)

    assert isinstance(timer, Timer)
    assert timer.get_count() == 1
    assert 0 < timer.get_value() < 0.05
    assert 0 < timer.get_mean_tick_time() < 0.05


@pytest.mark.parametrize("call_count", [1, 2, 3, 10, 20, 30, 100, 200, 300])
def test_count_decorator_updates_existing_counter(call_count: int) -> None:
    timer_name = "mock_function"

    assert registry.get_timer(timer_name) is None

    for _ in range(call_count):
        mock_function()

    timer = registry.get_timer(timer_name)

    assert isinstance(timer, Timer)
    assert timer.get_count() == call_count
    assert 0 < timer.get_mean_tick_time() < 0.05


def test_time_decorator_with_name() -> None:
    @time(name="test_timer_meter")
    def mock() -> None:
        print("Mock method")

    mock()

    assert "test_timer_meter" in registry.METERS[MeterType.TIMER]
