import pytest

from pylemetry import registry
from pylemetry.meters import Counter, Gauge, Timer, MeterType


def test_add_counter() -> None:
    counter = Counter()
    counter_name = "test_counter"

    registry.add_counter(counter_name, counter)

    assert len(registry.METERS[MeterType.COUNTER]) == 1
    assert counter_name in registry.METERS[MeterType.COUNTER]
    assert registry.METERS[MeterType.COUNTER][counter_name] == counter


def test_add_counter_already_exists() -> None:
    counter = Counter()
    counter_name = "test_counter"

    registry.add_counter(counter_name, counter)

    with pytest.raises(AttributeError) as exec_info:
        new_counter = Counter()

        registry.add_counter(counter_name, new_counter)

    assert exec_info.value.args[0] == f"A counter with the name '{counter_name}' already exists"


def test_get_counter() -> None:
    counter = Counter()
    counter_name = "test_counter"

    registry.add_counter(counter_name, counter)

    new_counter = registry.get_counter(counter_name)

    assert new_counter == counter


def test_remove_counter() -> None:
    counter = Counter()
    counter_name = "test_counter"

    registry.add_counter(counter_name, counter)

    assert counter_name in registry.METERS[MeterType.COUNTER]

    registry.remove_counter(counter_name)

    assert len(registry.METERS[MeterType.COUNTER]) == 0
    assert counter_name not in registry.METERS[MeterType.COUNTER]


def test_add_gauge() -> None:
    gauge = Gauge()
    gauge_name = "test_gauge"

    registry.add_gauge(gauge_name, gauge)

    assert len(registry.METERS[MeterType.GAUGE]) == 1
    assert gauge_name in registry.METERS[MeterType.GAUGE]
    assert registry.METERS[MeterType.GAUGE][gauge_name] == gauge


def test_add_gauge_already_exists() -> None:
    gauge = Gauge()
    gauge_name = "test_gauge"

    registry.add_gauge(gauge_name, gauge)

    with pytest.raises(AttributeError) as exec_info:
        new_gauge = Gauge()

        registry.add_gauge(gauge_name, new_gauge)

    assert exec_info.value.args[0] == f"A gauge with the name '{gauge_name}' already exists"


def test_get_gauge() -> None:
    gauge = Gauge()
    gauge_name = "test_gauge"

    registry.add_gauge(gauge_name, gauge)

    new_gauge = registry.get_gauge(gauge_name)

    assert new_gauge == gauge


def test_remove_gauge() -> None:
    gauge = Gauge()
    gauge_name = "test_gauge"

    registry.add_gauge(gauge_name, gauge)

    assert gauge_name in registry.METERS[MeterType.GAUGE]

    registry.remove_gauge(gauge_name)

    assert len(registry.METERS[MeterType.GAUGE]) == 0
    assert gauge_name not in registry.METERS[MeterType.GAUGE]


def test_add_timer() -> None:
    timer = Timer()
    timer_name = "test_timer"

    registry.add_timer(timer_name, timer)

    assert len(registry.METERS[MeterType.TIMER]) == 1
    assert timer_name in registry.METERS[MeterType.TIMER]
    assert registry.METERS[MeterType.TIMER][timer_name] == timer


def test_add_timer_already_exists() -> None:
    timer = Timer()
    timer_name = "test_timer"

    registry.add_timer(timer_name, timer)

    with pytest.raises(AttributeError) as exec_info:
        new_timer = Timer()

        registry.add_timer(timer_name, new_timer)

    assert exec_info.value.args[0] == f"A timer with the name '{timer_name}' already exists"


def test_get_timer() -> None:
    timer = Timer()
    timer_name = "test_timer"

    registry.add_timer(timer_name, timer)

    new_timer = registry.get_timer(timer_name)

    assert new_timer == timer


def test_remove_timer() -> None:
    timer = Timer()
    timer_name = "test_timer"

    registry.add_timer(timer_name, timer)

    assert timer_name in registry.METERS[MeterType.TIMER]

    registry.remove_timer(timer_name)

    assert len(registry.METERS[MeterType.TIMER]) == 0
    assert timer_name not in registry.METERS[MeterType.TIMER]


def test_clear_registry() -> None:
    counter = Counter()
    counter_name = "test_counter"

    gauge = Gauge()
    gauge_name = "test_gauge"

    timer = Timer()
    timer_name = "test_timer"

    registry.add_counter(counter_name, counter)
    registry.add_gauge(gauge_name, gauge)
    registry.add_timer(timer_name, timer)

    assert counter_name in registry.METERS[MeterType.COUNTER]
    assert gauge_name in registry.METERS[MeterType.GAUGE]
    assert timer_name in registry.METERS[MeterType.TIMER]

    registry.clear()

    assert len(registry.METERS[MeterType.COUNTER]) == 0
    assert len(registry.METERS[MeterType.GAUGE]) == 0
    assert len(registry.METERS[MeterType.TIMER]) == 0

    assert counter_name not in registry.METERS[MeterType.COUNTER]
    assert gauge_name not in registry.METERS[MeterType.GAUGE]
    assert timer_name not in registry.METERS[MeterType.TIMER]
