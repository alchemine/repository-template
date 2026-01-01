"""DepthLogger class.

Log depth of code.
"""

import inspect
import contextlib
from collections import defaultdict
from functools import wraps

from src.common.timer import Timer


class DepthManager(contextlib.ContextDecorator):
    """Code Depth Manager.

    Attributes:
        depth (int): Current depth of code
        depths (dict): Depths of codes
    """

    depth = 1
    depths = defaultdict(lambda: 1)

    @classmethod
    def __enter__(cls):
        cls.depth += 1
        return cls

    @classmethod
    def __exit__(cls, *exc):
        cls.depths[cls.depth] = 1  # reset
        cls.depth -= 1
        cls.depths[cls.depth] += 1
        return False

    @classmethod
    async def __aenter__(cls):
        return cls.__enter__()

    @classmethod
    async def __aexit__(cls, *exc):
        return cls.__exit__(*exc)


def D(fn):
    """Depth logging decorator.

    Example:
        >>> @D
        >>> def f():
        ...     # Depth: 1
        ...     g()
        >>> @D
        >>> def g():
        ...     # Depth: 2
        ...     # do something
    """

    def _format_name(args, fn):
        """Print depth of code.

        Args:
            name (str): Function name
            args (tuple): Arguments of the function
            fn (callable): Function
        """
        name = ".".join(
            [str(DepthManager.depths[d]) for d in range(1, DepthManager.depth + 1)]
        )
        index = f"{name:17}| "
        if len(args) > 0 and isinstance(
            args[0], object
        ):  # if function is method or main function
            index = f"{index}{fn.__module__.split('.')[-1]}."
        fn_name = fn.__name__
        return f"{index}{fn_name}"

    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def _log(*args, **kwargs):
            async with DepthManager():
                async with Timer(_format_name(args, fn)):
                    return await fn(*args, **kwargs)

    else:

        @wraps(fn)
        def _log(*args, **kwargs):
            with DepthManager():
                with Timer(_format_name(args, fn)):
                    return fn(*args, **kwargs)

    return _log
