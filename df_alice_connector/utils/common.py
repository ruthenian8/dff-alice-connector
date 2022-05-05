import sys
from functools import wraps
from urllib import parse
from typing import Union, Callable
from numbers import Number


def get_positive_hash(any_string: str) -> str:
    return str(hash(any_string) + sys.maxsize + 1)


def compare_func(item: Union[dict, Number], candidates: list, full_match: bool = True) -> bool:
    if isinstance(item, Number):
        return any(map(lambda x: x == item, candidates))

    for candidate in candidates:
        print("item: " + str(item))
        print("candidate: " + str(candidate))
        intersection = item.items() & candidate.items()
        if intersection:
            if full_match and len(intersection) != len(candidate):
                return False
            return True
    return False


def quote_url(url: str):
    return parse.quote(url, safe="~@#$&()*!+=:;,.?/'")


def partialmethod(func: Callable, **part_kwargs):
    """
    This function replaces the partialmethod implementation from functools.
    In contrast with the original class-based approach, it decorates the function, so we can use docstrings.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **part_kwargs, **kwargs)

    wrapper.__doc__ = func.__doc__.format(**part_kwargs)

    return wrapper
