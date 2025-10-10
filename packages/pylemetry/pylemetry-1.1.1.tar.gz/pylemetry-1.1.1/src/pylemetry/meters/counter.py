from pylemetry.meters.meter import Meter, MeterType


class Counter(Meter):
    def __init__(self):
        super().__init__(MeterType.COUNTER)

    def add(self, value: int = 1) -> None:
        """
        Add a value to the count within this counter

        :param value: Value to add, default 1
        """

        with self.lock:
            self.value += value

    def __add__(self, other: int) -> "Counter":
        self.add(other)

        return self
