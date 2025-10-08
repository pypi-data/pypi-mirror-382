from functools import wraps
from typing import Callable, Iterator, ParamSpec, TypeVar

_P = ParamSpec("_P")
_Item = TypeVar("_Item")


def listify(func: Callable[_P, Iterator[_Item]]) -> Callable[_P, list[_Item]]:
    """Decorator for making a generator return a list instead."""

    @wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs):
        return list(func(*args, **kwargs))

    return wrapper
