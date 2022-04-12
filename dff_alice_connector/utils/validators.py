import sys
from typing import Callable

from pydantic import ValidationError


def get_size_validator(req_size: int) -> Callable:
    def check_url(cls, item):
        size = sys.getsizeof(item)
        if not size <= req_size:
            raise ValidationError(f"The object should have at most {str(req_size)} bytes, got {size}.")
        return item

    return check_url


def get_len_validator(req_len: int) -> Callable:
    def check_sequence(cls, sequence):
        seq_len = len(sequence)
        if not seq_len <= req_len:
            raise ValidationError(f"The sequence should contain at most {str(req_len)} items or chars, got {seq_len}.")
        return sequence

    return check_sequence
