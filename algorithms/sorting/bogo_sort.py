"""
Bogo Sort

Bogo sort repeatedly shuffles the array at random until it happens to be
sorted.  It is extremely inefficient and used only for educational purposes.

Reference: https://en.wikipedia.org/wiki/Bogosort

Complexity:
    Time:  O(n) best / O(n * n!) average / O(infinity) worst
    Space: O(1)
"""

from __future__ import annotations

import random


def bogo_sort(array: list[int]) -> list[int]:
    """Sort an array in ascending order using bogo sort.

    The algorithm works in two phases that repeat until the decisive
    transition occurs:

    1. **Check** – ``_is_sorted`` scans the array in O(n).  If every
       adjacent pair satisfies ``a[i] <= a[i+1]`` the loop exits
       immediately (this is the decisive state transition).
    2. **Shuffle** – ``random.shuffle`` rearranges elements uniformly at
       random, discarding all previous intermediate states.

    For [3, 1, 2] one possible execution (seed=0) looks like::

        attempt 1: [3, 1, 2] → not sorted → shuffle
        attempt 2: [2, 3, 1] → not sorted → shuffle
        attempt 3: [1, 2, 3] → sorted     → return

    The intermediate shuffle results are non-deterministic; only the
    final sorted state is guaranteed.

    Args:
        array: List of integers to sort.  The list is mutated in-place;
               the same object is returned.

    Returns:
        The same list object, sorted in non-decreasing (ascending) order.

    Examples:
        >>> import random; random.seed(0)
        >>> bogo_sort([3, 1, 2])
        [1, 2, 3]
        >>> random.seed(0)
        >>> bogo_sort([1, 2, 3])
        [1, 2, 3]
        >>> random.seed(0)
        >>> bogo_sort([2, 2, 1])
        [1, 2, 2]
        >>> random.seed(42)
        >>> bogo_sort([3, 2, 1])
        [1, 2, 3]
        >>> bogo_sort([1])
        [1]
    """
    while not _is_sorted(array):
        random.shuffle(array)
    return array


def _is_sorted(array: list[int]) -> bool:
    """Return True if *array* is in non-decreasing order."""
    return all(
        array[i] <= array[i + 1] for i in range(len(array) - 1)
    )
