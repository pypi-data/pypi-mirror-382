from typing import Callable, Any, Optional

from functools import wraps

from pylemetry import registry
from pylemetry.meters import Timer


def time(name: Optional[str] = None) -> Callable[..., Any]:
    """
    Decorator to time the invocations of a given callable. Creates a Timer meter in the Registry with either the
    provided name or the fully qualified name of the callable object as the metric name.

    :param name: Name of the meter to create, if None the function name is used
    :return: Result of the wrapped function
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapper() -> Any:
            time_name = f.__qualname__ if name is None else name

            _timer = registry.get_timer(time_name)

            if not _timer:
                _timer = Timer()
                registry.add_timer(time_name, _timer)

            with _timer.time():
                return f()

        return wrapper

    return decorator
