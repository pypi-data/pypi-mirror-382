import logging
import time

import pytest

from pylemetry import registry
from pylemetry.meters import Counter, Gauge, Timer
from pylemetry.reporting import Reporter, LoggingReporter, ReportingType


def test_reporter_base_class_cant_flush() -> None:
    with pytest.raises(NotImplementedError):
        reporter = Reporter(1)
        reporter.flush()


def test_reporter_flushing_on_timer(caplog) -> None:
    logger = logging.getLogger(__name__)

    counter = Counter()
    counter += 1

    registry.add_counter("test_counter", counter)

    with caplog.at_level(logging.INFO):
        reporter = LoggingReporter(0.1, logger, logging.INFO, ReportingType.CUMULATIVE)
        reporter.start()

        time.sleep(0.5)

        reporter.stop()

        assert len(caplog.records) == 5


def test_message_format_counter() -> None:
    message_format = (
        "{{'name': '{name}', 'type': '{type}', 'value': {value}, 'min': {min}, 'max': {max}, 'average': {avg}}}"
    )

    counter = Counter()
    counter += 10

    message = Reporter.format_message(message_format, "test_counter", counter, False)

    assert (
        message
        == "{'name': 'test_counter', 'type': 'counter', 'value': 10.0, 'min': 10.0, 'max': 10.0, 'average': 10.0}"
    )


def test_message_format_gauge() -> None:
    message_format = (
        "{{'name': '{name}', 'type': '{type}', 'value': {value}, 'min': {min}, 'max': {max}, 'average': {avg}}}"
    )

    gauge = Gauge()
    gauge += 10

    message = Reporter.format_message(message_format, "test_gauge", gauge, False)

    assert (
        message == "{'name': 'test_gauge', 'type': 'gauge', 'value': 10.0, 'min': 10.0, 'max': 10.0, 'average': 10.0}"
    )


def test_message_format_timer() -> None:
    message_format = (
        "{{'name': '{name}', 'type': '{type}', 'value': {value}, 'count': {count}, 'min': {min}, "
        "'max': {max}, 'average': {avg}}}"
    )

    timer = Timer()
    timer.ticks = [1, 2, 3, 4, 5]

    message = Reporter.format_message(message_format, "test_timer", timer, False)

    assert (
        message
        == "{'name': 'test_timer', 'type': 'timer', 'value': 15, 'count': 5, 'min': 1, 'max': 5, 'average': 3.0}"
    )


def test_message_format_unsupported_meter() -> None:
    with pytest.raises(ValueError) as exec_info:
        Reporter.format_message("Hello World!", "test_meter", "fake meter", False)  # type: ignore

    assert exec_info.value.args[0] == "Unsupported meter of type <class 'str'>"
