from typing import Generator

import time

from contextlib import contextmanager

from pylemetry.meters.meter import Meter, MeterType


class Timer(Meter):
    def __init__(self):
        super().__init__(MeterType.TIMER)

        self.ticks = []

    def tick(self, tick: float) -> None:
        """
        Add a value to the list of ticks within this timer

        :param tick: Value to add to the ticks list
        """

        with self.lock:
            self.ticks.append(tick)

    @contextmanager
    def time(self) -> Generator[None, None, None]:
        """
        Context manager to time in seconds a code block and add the result to the internal ticks list
        """

        start_time = time.perf_counter()

        try:
            yield
        finally:
            end_time = time.perf_counter()

            self.tick(end_time - start_time)

    def get_value(self, since_last_interval: bool = False) -> int:
        """
        Get the sum of all ticks within this timer

        :param since_last_interval: If true, returns the sum of all ticks since the last marked interval, otherwise
        returns the full value
        :return: Sum of all ticks
        """

        ticks = self.get_ticks_since_last_interval() if since_last_interval else self.ticks

        return sum(ticks)

    def get_count(self, since_last_interval: bool = False) -> int:
        """
        Get the count of the number of ticks within this timer

        :param since_last_interval: If true, returns the value since the last marked interval, otherwise returns the
        full value
        :return: Number of ticks
        """

        ticks = self.get_ticks_since_last_interval() if since_last_interval else self.ticks

        return len(ticks)

    def get_mean_tick_time(self, since_last_interval: bool = False) -> float:
        """
        Get the mean tick time from the list of ticks within this timer

        :param since_last_interval: If true, returns the value since the last marked interval, otherwise returns the
        full value
        :return: Mean tick time
        """

        ticks = self.get_ticks_since_last_interval() if since_last_interval else self.ticks

        if len(ticks) == 0:
            return 0

        return sum(ticks) / len(ticks)

    def get_max_tick_time(self, since_last_interval: bool = False) -> float:
        """
        Get the maximum tick time from the list of ticks within this timer

        :param since_last_interval: If true, returns the value since the last marked interval, otherwise returns the
        full value
        :return: Maximum tick time
        """

        ticks = self.get_ticks_since_last_interval() if since_last_interval else self.ticks

        if len(ticks) == 0:
            return 0

        return max(ticks)

    def get_min_tick_time(self, since_last_interval: bool = False) -> float:
        """
        Get the minimum tick time from the list of ticks within this timer

        :param since_last_interval: If true, returns the value since the last marked interval, otherwise returns the
        full value
        :return: Minimum tick time
        """

        ticks = self.get_ticks_since_last_interval() if since_last_interval else self.ticks

        if len(ticks) == 0:
            return 0

        return min(ticks)

    def get_ticks_since_last_interval(self) -> list[float]:
        """
        Get a list of the ticks since the most recent marked interval

        :return: List of ticks since the most recent marked interval
        """

        return self.ticks[int(self.last_interval_value) :]

    def mark_interval(self) -> None:
        """
        Mark an interval and update the most recent interval value
        """

        with self.lock:
            self.last_interval_value = len(self.ticks)
