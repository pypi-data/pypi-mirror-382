from typing import Optional

from pylemetry.meters import Counter, Gauge, Timer, Meter, MeterType

METERS: dict[MeterType, dict[str, Meter]] = {
    MeterType.COUNTER: {},
    MeterType.GAUGE: {},
    MeterType.TIMER: {},
}


def clear() -> None:
    """
    Remove all meters from the global registry
    """

    for _, meters in METERS.items():
        meters.clear()


def add_meter(name: str, meter: Meter, meter_type: MeterType) -> None:
    """
    Add a meter to the global registry

    :param name: Unique name of the meter to add
    :param meter: Meter to add
    :param meter_type: Meter type of the meter to add

    :raises AttributeError: When the name provided for the meter of this type is already in use in the global registry
    """

    if name in METERS[meter_type]:
        raise AttributeError(f"A {meter_type.value} with the name '{name}' already exists")

    METERS[meter_type][name] = meter


def get_meter(name, meter_type: MeterType) -> Optional[Meter]:
    """
    Get a meter from the global registry by its name

    :param name: Name of the meter
    :param meter_type: Meter type of the meter to retrieve
    :return: Meter in the global registry
    """

    return METERS[meter_type].get(name)


def remove_meter(name, meter_type: MeterType) -> None:
    """
    Remove a meter from the global registry

    :param name: Name of the meter to remove
    :param meter_type: Meter type of the meter to remove
    """

    if name in METERS[meter_type]:
        del METERS[meter_type][name]


def add_counter(name: str, counter: Counter) -> None:
    """
    Add a counter to the global registry

    :param name: Unique name of the counter
    :param counter: Counter to add

    :raises AttributeError: When the name provided for the counter metric is already in use in the global registry
    """

    add_meter(name, counter, MeterType.COUNTER)


def get_counter(name: str) -> Optional[Counter]:
    """
    Get a counter from the global registry by its name

    :param name: Name of the counter
    :return: Counter in the global registry
    """

    return get_meter(name, MeterType.COUNTER)  # type: ignore


def remove_counter(name: str) -> None:
    """
    Remove a counter from the global registry

    :param name: Name of the counter to remove
    """

    remove_meter(name, MeterType.COUNTER)


def add_gauge(name: str, gauge: Gauge) -> None:
    """
    Add a gauge to the global registry

    :param name: Unique name of the gauge
    :param gauge: Gauge to add

    :raises AttributeError: When the name provided for the gauge metric is already in use in the global registry
    """

    add_meter(name, gauge, MeterType.GAUGE)


def get_gauge(name: str) -> Optional[Gauge]:
    """
    Get a gauge from the global registry by its name

    :param name: Name of the gauge
    :return: Gauge in the global registry
    """

    return get_meter(name, MeterType.GAUGE)  # type: ignore


def remove_gauge(name: str) -> None:
    """
    Remove a gauge from the global registry

    :param name: Name of the gauge to remove
    """

    remove_meter(name, MeterType.GAUGE)


def add_timer(name: str, timer: Timer) -> None:
    """
    Add a timer to the global registry

    :param name: Unique name of the timer
    :param timer: Timer to add

    :raises AttributeError: When the name provided for the timer metric is already in use in the global registry
    """

    add_meter(name, timer, MeterType.TIMER)


def get_timer(name: str) -> Optional[Timer]:
    """
    Get a timer from the global registry by its name

    :param name: Name of the timer
    :return: Timer in the global registry
    """

    return get_meter(name, MeterType.TIMER)  # type: ignore


def remove_timer(name: str) -> None:
    """
    Remove a timer from the global registry

    :param name: Name of the timer to remove
    """

    remove_meter(name, MeterType.TIMER)
