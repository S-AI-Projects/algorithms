"""
Josephus Problem

People sit in a circular fashion; every k-th person is eliminated until
everyone has been removed. Yield the elimination order.

Reference: https://en.wikipedia.org/wiki/Josephus_problem

Complexity:
    Time:  O(n^2) due to list.pop at arbitrary index
    Space: O(1) auxiliary (yields in-place)
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any


def josephus(items: list[Any], skip: int) -> Generator[Any, None, None]:
    """Yield elements eliminated in Josephus-problem order.

    Contract & Invariants:
        - In-place mutation: The caller-supplied list `items` is consumed in place
          via `.pop()`; upon generator exhaustion, `len(items) == 0`.
        - Permutation Invariant: For any non-empty list of unique elements and skip >= 1,
          the yielded sequence is a valid permutation of the original elements
          (len(result) == len(original) and set(result) == set(original)).
        - Recurrence Invariant: The final yielded element (the survivor) strictly matches
          the closed-form Josephus recurrence J(n, k) = (J(n - 1, k) + k) % n.
        - Identity case: When skip == 1, elements are yielded in original sequential order.

    Args:
        items: List of participants arranged in a circle.
        skip: Every *skip*-th person is eliminated each round (skip >= 1).

    Returns:
        A generator yielding eliminated elements in order.

    Examples:
        >>> list(josephus([1, 2, 3, 4, 5, 6, 7, 8, 9], 3))
        [3, 6, 9, 4, 8, 5, 2, 7, 1]
        >>> list(josephus([1, 2, 3, 4, 5, 6, 7, 8, 9], 2))
        [2, 4, 6, 8, 1, 5, 9, 7, 3]
    """
    skip = skip - 1
    index = 0
    remaining = len(items)
    while remaining > 0:
        index = (skip + index) % remaining
        yield items.pop(index)
        remaining -= 1
