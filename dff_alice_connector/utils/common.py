import sys
from urllib import parse
from typing import Union
from numbers import Number


def get_positive_hash(any_string: str) -> str:
    return str(hash(any_string) + sys.maxsize + 1)


def compare_func(item: Union[dict, Number], candidates: list, full_match: bool = True) -> bool:
    if isinstance(item, Number):
        return any(map(lambda x: x == item, candidates))

    for candidate in candidates:
        intersection = item.items() & candidate.items()
        if intersection:
            if full_match and len(intersection) != len(candidate):
                return False
            return True
    return False


def quote_url(url: str):
    return parse.quote(url, safe="~@#$&()*!+=:;,.?/'")
