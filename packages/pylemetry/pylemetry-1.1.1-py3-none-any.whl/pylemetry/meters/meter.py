from enum import Enum
from threading import Lock


class MeterType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    TIMER = "timer"


class Meter:
    def __init__(self, meter_type: MeterType):
        self.lock = Lock()
        self.value = 0.0
        self.last_interval_value = 0.0
        self.meter_type = meter_type

    def get_value(self, since_last_interval: bool = False) -> float:
        """
        Get the value from this meter

        :param since_last_interval: If true, returns the value since the last marked interval, otherwise returns the
        full value
        :return: Value from this meter
        """

        if since_last_interval:
            return self.value - self.last_interval_value
        else:
            return self.value

    def mark_interval(self) -> None:
        """
        Mark an interval and update the most recent interval value
        """

        with self.lock:
            self.last_interval_value = self.value
