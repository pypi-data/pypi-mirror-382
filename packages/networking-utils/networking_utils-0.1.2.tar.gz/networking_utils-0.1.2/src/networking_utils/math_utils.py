"""Math utility functions for networking_utils.

Currently contains a simple add_two_number function, with type hints and a small self-test.
"""
from __future__ import annotations

from typing import Union

Number = Union[int, float]

def add_two_number(a: Number, b: Number) -> Number:
    """Return the sum of two numbers.

    Examples
    --------
    >>> add_two_number(2, 3)
    5
    >>> add_two_number(2.5, 0.5)
    3.0
    """
    return a + b

if __name__ == "__main__":  # pragma: no cover
    print("Self-test: add_two_number(2, 3) ->", add_two_number(2, 3))
