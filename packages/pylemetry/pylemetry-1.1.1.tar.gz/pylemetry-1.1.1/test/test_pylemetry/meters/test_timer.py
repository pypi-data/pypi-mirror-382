import pytest
import time

from pylemetry.meters import Timer


def test_timer_count_starts_at_0() -> None:
    timer = Timer()

    assert timer.get_value() == 0


@pytest.mark.parametrize("value", [1, 2, 3, 1.5, 2.5, 3.5, 10, 20, 30])
def test_timer_tick(value: float) -> None:
    timer = Timer()

    timer.tick(value)

    assert timer.get_count() == 1
    assert timer.get_value() == value
    assert timer.get_mean_tick_time() == value


def test_time() -> None:
    timer = Timer()

    with timer.time():
        time.sleep(0.25)

    assert timer.get_count() == 1
    assert 0.25 <= timer.get_value() < 0.5
    assert 0.25 <= timer.get_mean_tick_time() < 0.5


def test_get_mean_tick_time() -> None:
    timer = Timer()

    timer.ticks = [1, 2, 3, 4, 5]

    assert timer.get_mean_tick_time() == 3


def test_get_max_tick_time() -> None:
    timer = Timer()

    timer.ticks = [1, 2, 3, 4, 5]

    assert timer.get_max_tick_time() == 5


def test_get_min_tick_time() -> None:
    timer = Timer()

    timer.ticks = [1, 2, 3, 4, 5]

    assert timer.get_min_tick_time() == 1


def test_get_timer_values_since_interval() -> None:
    timer = Timer()

    timer.ticks = [1, 2, 3, 4, 5]

    assert timer.get_count() == 5
    assert timer.get_value() == 15
    assert timer.get_min_tick_time() == 1
    assert timer.get_mean_tick_time() == 3
    assert timer.get_max_tick_time() == 5

    timer.mark_interval()

    assert timer.get_count() == 5
    assert timer.get_value() == 15
    assert timer.get_min_tick_time() == 1
    assert timer.get_mean_tick_time() == 3
    assert timer.get_max_tick_time() == 5

    assert timer.get_count(since_last_interval=True) == 0
    assert timer.get_value(since_last_interval=True) == 0
    assert timer.get_min_tick_time(since_last_interval=True) == 0
    assert timer.get_mean_tick_time(since_last_interval=True) == 0
    assert timer.get_max_tick_time(since_last_interval=True) == 0
