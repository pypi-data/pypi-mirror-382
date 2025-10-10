import pytest

from pylemetry.meters import Gauge


def test_gauge_starts_at_0() -> None:
    gauge = Gauge()

    assert gauge.get_value() == 0.0


@pytest.mark.parametrize("value", [1, 2, 3, 1.5, 2.5, 3.5, 10, 20, 30])
def test_gauge_set_value(value: float) -> None:
    gauge = Gauge()

    gauge.set_value(value)

    assert gauge.get_value() == value


@pytest.mark.parametrize("value", [1, 2, 3, 1.5, 2.5, 3.5, 10, 20, 30])
def test_gauge_add(value: float) -> None:
    gauge = Gauge()

    gauge.add(value)

    assert gauge.get_value() == value


@pytest.mark.parametrize("value", [1, 2, 3, 1.5, 2.5, 3.5, 10, 20, 30])
def test_gauge_dunder_add(value: float) -> None:
    gauge = Gauge()

    gauge += value

    assert gauge.get_value() == value


@pytest.mark.parametrize("value", [1, 2, 3, 1.5, 2.5, 3.5, 10, 20, 30])
def test_gauge_subtract(value: float) -> None:
    gauge = Gauge()

    gauge.subtract(value)

    assert gauge.get_value() == -value


@pytest.mark.parametrize("value", [1, 2, 3, 1.5, 2.5, 3.5, 10, 20, 30])
def test_gauge_dunder_sub(value: float) -> None:
    gauge = Gauge()

    gauge -= value

    assert gauge.get_value() == -value


def test_gauge_value_since_interval() -> None:
    gauge = Gauge()
    gauge += 10

    assert gauge.get_value() == 10

    gauge.mark_interval()

    assert gauge.get_value() == 10
    assert gauge.get_value(since_last_interval=True) == 0
