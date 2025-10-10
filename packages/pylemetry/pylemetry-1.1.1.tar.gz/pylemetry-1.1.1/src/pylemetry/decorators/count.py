from typing import Callable, Any, Optional

from functools import wraps

from pylemetry import registry
from pylemetry.meters import Counter


def count(name: Optional[str] = None) -> Callable[..., Any]:
    """
    Decorator to count the number of invocations of a given callable. Creates a Counter meter in the Registry
    with either the provided name or the fully qualified name of the callable object as the metric name.

    :param name: Name of the meter to create, if None the function name is used
    :return: Result of the wrapped function
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapper() -> Any:
            counter_name = f.__qualname__ if name is None else name

            counter = registry.get_counter(counter_name)

            if not counter:
                counter = Counter()
                registry.add_counter(counter_name, counter)

            counter += 1

            return f()

        return wrapper

    return decorator
