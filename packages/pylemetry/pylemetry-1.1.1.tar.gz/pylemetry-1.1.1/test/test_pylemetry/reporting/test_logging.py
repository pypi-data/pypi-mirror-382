import logging
import time

import pytest
from logot import Logot, logged
from logot.loguru import LoguruCapturer
from loguru import logger as loguru_logger

from pylemetry import registry
from pylemetry.meters import Counter, Gauge, Timer, MeterType
from pylemetry.reporting import LoggingReporter, ReportingType


@pytest.mark.parametrize(
    "level", [logging.DEBUG, logging.INFO, logging.WARNING, logging.WARN, logging.ERROR, logging.CRITICAL]
)
def test_logging_reporter_logs_messages(caplog, level: int) -> None:
    logger = logging.getLogger(__name__)

    counter = Counter()
    counter += 1

    registry.add_counter("test_counter", counter)

    with caplog.at_level(level):
        reporter = LoggingReporter(10, logger, level, ReportingType.CUMULATIVE)
        reporter.configure_message_format("Hello World!")
        reporter.flush()

    assert "Hello World!" in caplog.text


def test_logging_reporter_loguru_compatibility() -> None:
    counter = Counter()
    counter += 1

    registry.add_counter("test_counter", counter)

    with Logot().capturing(capturer=LoguruCapturer) as logot:
        reporter = LoggingReporter(10, loguru_logger, logging.INFO, ReportingType.CUMULATIVE)
        reporter.configure_message_format("Hello World!")
        reporter.flush()

        logot.assert_logged(logged.info("Hello World!"))


def test_logging_default_message_formats(caplog) -> None:
    logger = logging.getLogger(__name__)

    counter = Counter()
    counter += 1

    gauge = Gauge()
    gauge += 1

    timer = Timer()
    timer.ticks = [1, 2, 3, 4, 5]

    registry.add_counter("test_counter", counter)
    registry.add_gauge("test_gauge", gauge)
    registry.add_timer("test_timer", timer)

    with caplog.at_level(logging.INFO):
        reporter = LoggingReporter(10, logger, logging.INFO, ReportingType.CUMULATIVE)
        reporter.flush()

    assert "test_counter [counter] -- 1" in caplog.text
    assert "test_gauge [gauge] -- 1" in caplog.text
    assert "test_timer [timer] -- 15" in caplog.text


def test_logging_configure_message_format_all_meters(caplog) -> None:
    logger = logging.getLogger(__name__)

    counter = Counter()
    counter += 1

    gauge = Gauge()
    gauge += 1

    timer = Timer()
    timer.ticks = [1, 2, 3, 4, 5]

    registry.add_counter("test_counter", counter)
    registry.add_gauge("test_gauge", gauge)
    registry.add_timer("test_timer", timer)

    with caplog.at_level(logging.INFO):
        reporter = LoggingReporter(10, logger, logging.INFO, ReportingType.CUMULATIVE)
        reporter.configure_message_format("{name} [{type}] {value}")
        reporter.flush()

    assert "test_counter [counter] 1" in caplog.text
    assert "test_gauge [gauge] 1" in caplog.text
    assert "test_timer [timer] 15" in caplog.text


def test_logging_configure_message_format_specific_meter_type(caplog) -> None:
    logger = logging.getLogger(__name__)

    counter = Counter()
    counter += 1

    gauge = Gauge()
    gauge += 1

    timer = Timer()
    timer.ticks = [1, 2, 3, 4, 5]

    registry.add_counter("test_counter", counter)
    registry.add_gauge("test_gauge", gauge)
    registry.add_timer("test_timer", timer)

    with caplog.at_level(logging.INFO):
        reporter = LoggingReporter(10, logger, logging.INFO, ReportingType.CUMULATIVE)
        reporter.configure_message_format("{name} [{type}] {value}", MeterType.COUNTER)
        reporter.flush()

    assert "test_counter [counter] 1" in caplog.text
    assert "test_gauge [gauge] -- 1" in caplog.text
    assert "test_timer [timer] -- 15" in caplog.text


def test_logging_reporter_marks_meter_intervals() -> None:
    logger = logging.getLogger(__name__)

    counter = Counter()
    counter += 1

    registry.add_counter("test_counter", counter)

    registry_counter = registry.get_counter("test_counter")

    assert registry_counter is not None
    assert registry_counter.get_value() == 1
    assert registry_counter.get_value(since_last_interval=True) == 1

    reporter = LoggingReporter(0.1, logger, logging.INFO, ReportingType.INTERVAL)
    reporter.start()

    time.sleep(0.5)

    registry_counter = registry.get_counter("test_counter")

    assert registry_counter is not None
    assert registry_counter.get_value() == 1
    assert registry_counter.get_value(since_last_interval=True) == 0

    registry_counter.add(1)

    assert registry_counter.get_value() == 2
    assert registry_counter.get_value(since_last_interval=True) == 1

    reporter.stop()

    registry_counter = registry.get_counter("test_counter")

    assert registry_counter is not None
    assert registry_counter.get_value() == 2
    assert registry_counter.get_value(since_last_interval=True) == 0
