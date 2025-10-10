# Pylemetry

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![image](https://img.shields.io/pypi/v/pylemetry.svg)](https://pypi.python.org/pypi/pylemetry)
[![image](https://img.shields.io/pypi/l/pylemetry.svg)](https://pypi.python.org/pypi/pylemetry)
[![image](https://img.shields.io/pypi/pyversions/pylemetry.svg)](https://pypi.python.org/pypi/pylemetry)
[![Release](https://github.com/amurphy4/pylemetry/actions/workflows/release.yaml/badge.svg?branch=main)](https://github.com/amurphy4/pylemetry/actions/workflows/release.yaml)

Add metrics to your Python applications with Pylemetry

Currently, three meters are supported, `Counter`, `Gauge`, and `Timer`

## Counter

The counter meter allows you to keep track of the number of times a block of code is executed.
A `Counter` can be created either directly

```python
from pylemetry.meters import Counter


def some_method() -> None:
    counter = Counter()

    for _ in range(100):
        counter.add()  # counter += 1 is also supported

    counter.get_value()  # 100
```

or via a decorator

```python
from pylemetry import registry
from pylemetry.decorators import count


@count()
def some_method() -> None:
    ...


@count("named_counter")
def another_method() -> None:
    ...


def main() -> None:
    for _ in range(100):
        some_method()
        another_method()

    counter = registry.get_counter("some_method")
    counter.get_value()  # 100

    counter = registry.get_counter("named_counter")
    counter.get_value()  # 100
```

When using this meter via a decorator, the meter gets added to the global `registry`, with the method name it's decorating as the meter name. Alternatively, you can provide a name for the meter as a parameter to the decorator

## Gauge

A `Gauge` meter allows you to keep track of varying metrics, e.g. memory usage or items on a queue. This meter currently isn't supported as a decorator

```python
from pylemetry import registry
from pylemetry.meters import Gauge


def some_method() -> None:
    gauge = Gauge()
    
    registry.add_gauge("sample_gauge", gauge)
```

The `Gauge` supports incrementing, decrementing, and setting a value directly

```python
from pylemetry import registry


gauge = registry.get_gauge("sample_gauge")

gauge.add(10)
gauge += 1.5
gauge.get_value()  # 11.5

gauge.subtract(10)
gauge -= 8.5
gauge.get_value()  # -7

gauge.set_value(7.5)
gauge.get_value()  # 7.5
```

## Timer

A `Timer` meter allows for tracking the time taken for a block of code. This can be done either directly

```python
from pylemetry.meters import Timer


def some_method() -> None:
    timer = Timer()

    for _ in range(100):
        with timer.time():
            ...

    timer.get_count()  # 100
    timer.get_mean_tick_time()  # Mean execution time of the code block
```

or via a decorator

```python
from pylemetry import registry
from pylemetry.decorators import time


@time()
def some_method() -> None:
    ...


@time("named_timer")
def another_method() -> None:
    ...


def main() -> None:
    for _ in range(100):
        some_method()
        another_method()
        
    timer = registry.get_timer("some_method")
    timer.get_count()  # 100
    timer.get_value()  # Sum total execution time of the some_method function
    timer.get_mean_tick_time()  # Mean execution time of the some_method function
    timer.get_max_tick_time()  # Maximum execution time of the some_method function
    timer.get_min_tick_time()  # Minimum execution time of the some_method function

    timer = registry.get_timer("named_timer")
    timer.get_count()  # 100
    ...
```

When using this meter via a decorator, the meter gets added to the global `registry`, with the method name it's decorating as the meter name. Alternatively, you can provide a name for the meter as a parameter to the decorator

## The Registry

Pylemetry maintains a global registry of meters, allowing you to share a meter across multiple files, or reference metrics from a central location.
This registry is also used to keep track of all metrics created by decorators, with those meters registered using the method name they are decorating

```python
from pylemetry import registry
from pylemetry.meters import Counter, Gauge, Timer


counter = Counter()
gauge = Gauge()
timer = Timer()

registry.add_counter("example", counter)
registry.add_gauge("example", gauge)
registry.add_timer("example", timer)
```

Each meter type has an `add_meter`, `get_meter` and `remove_meter` method to manage meters in the `registry`, each requiring a unique meter name.
There is also a base method for each of these methods, accepting an additional parameter of `MeterType`

```python
from pylemetry import registry
from pylemetry.meters import Counter, MeterType


counter = Counter()

registry.add_meter("example", counter, MeterType.COUNTER)
registry.get_meter("example", MeterType.COUNTER)
registry.remove_meter("example", MeterType.COUNTER)
registry.get_meter("example", MeterType.COUNTER)  # None
```

The `registry` can be cleared through the `clear()` method

## Reporting

Periodic reporting of all meters in the registry can be achieved using the `LoggingReporter`. This reporter periodically logs messages to a provided logger with a given message format and interval.

### Message Formatting
The message format allows for substitutions for metric values with the following options

| Substitution Key | Effect                                                                                                                                        |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| name             | Name of the meter being logged                                                                                                                |
| value            | Value of the meter, `value` for `Counter` and `Gauge` meters, sum of all ticks for `Timer` meters                                             |
| count            | Value of the meter for `Counter` and `Gauge` meters, number of ticks for `Timer` meters                                                       |
| min              | Minimum value of the meter, equivalent to the `value` substitution for `Counter` and `Gauge` meters, `min_tick_time` for `Timer` meters       |
| max              | Maximum value of the meter, equivalent to the `value` substitution for `Counter` and `Gauge` meters, `max_tick_time` for `Timer` meters       |
| avg              | Mean average value of the meter, equivalent to the `value` substitution for `Counter` and `Gauge` meters, `mean_tick_time` for `Timer` meters |
| type             | Type of the meter (`counter`, `gauge`, or `timer`)                                                                                            |

As an example, a `Counter` meter named `sample_counter` with a value of 10
```python
message_format = "Meter: {name} - Value: {value}"
```
This message format would evaluate to `Meter: sample_counter - Value: 10`

It is possible to include braces `{}` in the message using the same rules as Python string formatting by doubling up the brace you want to escape.
```python
message_format = "{{'name': '{name}', 'value': {value}, 'extra': 'abc123'}}"
```
This message format would evaluate to `{'name': 'sample_counter', 'value': 10, 'extra': 'abc123'}`

### LoggingReporter

The `LoggingReporter` takes a provided logger, log level, message format, and interval, and logs formatted messages for all meters in the registry to the provided logger at the specified log level every `n` seconds where `n` is the provided interval.

Any logger can be used with the `LoggingReporter` so long as it conforms to the `Loggable` protocol defined in `pylemetry.reporters.logging`. 
The Python built in `logging` logger conforms to this, as do several alternate logging packages such as [Loguru](https://pypi.org/project/loguru/)

An additional parameter `ReportingType` is required to determine whether to log cumulatively, or per interval.
When `ReportingType.CUMULATIVE` is provided then all logs for all meters will include values for the meter's entire lifespan. 
If `ReportingType.INTERVAL` is provided, all meters will log only the changes in that meter since the most recent interval was marked, either manually or by the most recent log flush

To configure message formats, use the `configure_message_formats` method, optionally providing a `MeterType` for the meters that this message format should apply to. 
If no `MeterType` is provided, the message format will apply to all meters