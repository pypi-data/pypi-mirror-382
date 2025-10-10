import logging
from typing import Protocol, ParamSpec, TypeVar, Optional

from pylemetry import registry
from pylemetry.meters import MeterType
from pylemetry.reporting.reporter import Reporter
from pylemetry.reporting.reporting_type import ReportingType

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class Loggable(Protocol[P, R]):
    def debug(self, msg: str, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def info(self, msg: str, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def warning(self, msg: str, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def error(self, msg: str, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def critical(self, msg: str, *args: P.args, **kwargs: P.kwargs) -> R: ...


class LoggingReporter(Reporter):
    def __init__(self, interval: float, logger: Loggable, level: int, _type: ReportingType):
        super().__init__(interval)

        self.logger = logger
        self.level = level
        self._type = _type

        self.message_formats = {
            MeterType.COUNTER: "{name} [{type}] -- {value}",
            MeterType.GAUGE: "{name} [{type}] -- {value}",
            MeterType.TIMER: "{name} [{type}] -- {value}",
        }

    def configure_message_format(self, message_format: str, meter_type: Optional[MeterType] = None):
        if not meter_type:
            for _type in list(MeterType):
                self.message_formats[_type] = message_format
        else:
            self.message_formats[meter_type] = message_format

    def flush(self) -> None:
        since_last_interval = self._type == ReportingType.INTERVAL

        for _, meters in registry.METERS.items():
            for name, meter in meters.items():
                self._log(
                    self.format_message(self.message_formats[meter.meter_type], name, meter, since_last_interval),
                )

                if since_last_interval:
                    meter.mark_interval()

    def _log(self, message: str) -> None:
        # Check the log level manually for compatibility with libraries like Loguru
        if self.level == logging.DEBUG:
            self.logger.debug(message)
        elif self.level == logging.INFO:
            self.logger.info(message)
        elif self.level == logging.WARNING or self.level == logging.WARN:
            self.logger.warning(message)
        elif self.level == logging.ERROR:
            self.logger.error(message)
        elif self.level == logging.CRITICAL:
            self.logger.critical(message)
