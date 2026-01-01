"""Timer class.

Context and decorator form timer.
"""

import inspect
import contextlib
from functools import wraps
from time import perf_counter

from src.common import get_logger


logger = get_logger(__name__)


class Timer(contextlib.ContextDecorator):
    """Timer.

    Examples:
        >>> with Timer('Code1'):
        ...     sleep(1)
        * Code1        | 1.00s (0.02m)
    """

    def __init__(self, name="Elapsed time"):
        self.name = name.removesuffix("()") + "()"

    def __enter__(self):
        logger.info(f"START | {self.name}")
        self.start_time = perf_counter()
        return self

    def __exit__(self, *exc):
        elapsed_time = perf_counter() - self.start_time
        logger.info(f" END  | {self.name} ({elapsed_time:.2f}s)")
        return False

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, *exc):
        return self.__exit__(*exc)


def T(fn: callable) -> callable:
    """Timer decorator.

    Example:
        >>> @T
        >>> def f():
        ...     sleep(1)
        * Elapsed time | 1.00s (0.02m)
    """
    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def _log(*args, **kwargs):
            async with Timer(fn.__name__):
                return await fn(*args, **kwargs)

    else:

        @wraps(fn)
        def _log(*args, **kwargs):
            with Timer(fn.__name__):
                return fn(*args, **kwargs)

    return _log


if __name__ == "__main__":
    with Timer("ABB"):
        print("A")
