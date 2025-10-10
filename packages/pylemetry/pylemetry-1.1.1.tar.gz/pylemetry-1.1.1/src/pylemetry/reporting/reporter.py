from typing import Optional

import threading

from pylemetry.meters import Counter, Gauge, Timer, Meter


class Reporter:
    def __init__(self, interval: float):
        self.interval = interval
        self.__timer_thread: Optional[threading.Timer] = None
        self.running = False

    def flush(self) -> None:
        """
        Flush all meter values in the registry. If the reporter is configured using `ReporterType.INTERVAL`, this will
        mark an interval each time it runs and only flush the meter values since the most recent interval
        """

        raise NotImplementedError()

    def _run(self) -> None:
        self.running = False
        self.flush()
        self.start()

    def start(self) -> None:
        """
        Start running a thread timer with the provided interval to flush the meters periodically
        """

        if not self.running:
            self.__timer_thread = threading.Timer(self.interval, self._run)
            self.__timer_thread.start()
            self.running = True

    def stop(self) -> None:
        """
        Stop the thread timer and flush all meters for a final time
        """

        if self.__timer_thread is not None:
            self.__timer_thread.cancel()

        self.flush()
        self.running = False

    @staticmethod
    def format_message(message_format: str, meter_name: str, meter: Meter, since_last_interval: bool = False) -> str:
        """
        Format output messages with the following format options:
            - name: Name of the meter being logged
            - value: Counter or Gauge value, or Timer count
            - min: Counter or Gauge value, or Timer minimum tick value
            - max: Counter or Gauge value, or Timer maximum tick value
            - avg: Counter or Gauge value, or Timer mean tick value
            - type: Meter type

        :param message_format: Message format string
        :param meter_name: Name of the meter to be output
        :param meter: Meter to be output
        :param since_last_interval: If true, values since the last interval will be used. If false, the full value
        will be used
        :return: Formatted output message containing meter values
        """

        if isinstance(meter, Timer):
            message = message_format.format(
                name=meter_name,
                value=meter.get_value(since_last_interval),
                count=meter.get_count(since_last_interval),
                min=meter.get_min_tick_time(since_last_interval),
                max=meter.get_max_tick_time(since_last_interval),
                avg=meter.get_mean_tick_time(since_last_interval),
                type=meter.meter_type.value,
            )
        elif isinstance(meter, Counter) or isinstance(meter, Gauge):
            message = message_format.format(
                name=meter_name,
                value=meter.get_value(since_last_interval),
                count=meter.get_value(since_last_interval),
                min=meter.get_value(since_last_interval),
                max=meter.get_value(since_last_interval),
                avg=meter.get_value(since_last_interval),
                type=meter.meter_type.value,
            )
        else:
            raise ValueError(f"Unsupported meter of type {type(meter)}")

        return message
