import pytest

from pylemetry.meters import Counter


def test_counter_starts_at_0() -> None:
    counter = Counter()

    assert counter.get_value() == 0


def test_counter_add_default() -> None:
    counter = Counter()
    counter.add()

    assert counter.get_value() == 1


@pytest.mark.parametrize("value", [1, 2, 3, 10, 20, 30, 100, 200, 300])
def test_counter_add(value: int) -> None:
    counter = Counter()
    counter.add(value)

    assert counter.get_value() == value


@pytest.mark.parametrize("value", [1, 2, 3, 10, 20, 30, 100, 200, 300])
def test_counter_dunder_add(value: int) -> None:
    counter = Counter()
    counter += value

    assert counter.get_value() == value


def test_counter_value_since_interval() -> None:
    counter = Counter()
    counter += 10

    assert counter.get_value() == 10

    counter.mark_interval()

    assert counter.get_value() == 10
    assert counter.get_value(since_last_interval=True) == 0
