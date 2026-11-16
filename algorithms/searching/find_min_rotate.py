"""
Find Minimum in Rotated Sorted Array

Find the minimum element in a sorted array that has been rotated at some
unknown pivot. Assumes no duplicates exist in the array.

Reference: https://en.wikipedia.org/wiki/Binary_search_algorithm

Complexity:
    Time:  O(1) best / O(log n) average / O(log n) worst
    Space: O(1) iterative, O(log n) recursive
"""

from __future__ import annotations


def find_min_rotate(array: list[int]) -> int:
    """Find the minimum element in a rotated sorted array (iterative).

    Contract:
        Supported input is a non-empty list of unique values in ascending
        order, rotated by any number of positions (zero included). Lists
        with duplicates are outside this domain (see the module docstring).
        The smallest value is returned (not its index), and ``array`` is
        only read, never modified.

    Worked example, ``[4, 5, 6, 7, 0, 1, 2]``:
        - low=0, high=6, mid=3: 7 > 2, so the minimum is right of mid and
          low becomes 4.
        - low=4, high=6, mid=5: 1 <= 2, so the minimum is at mid or left of
          it and high becomes 5.
        - low=4, high=5, mid=4: 0 <= 1, so high becomes 4.
        - low == high == 4, so ``array[4]``, which is 0, is returned.

    Args:
        array: A sorted list of unique integers that has been rotated.

    Returns:
        The minimum value in the array.

    Examples:
        >>> find_min_rotate([4, 5, 6, 7, 0, 1, 2])
        0
        >>> find_min_rotate([1, 2, 3])
        1
        >>> find_min_rotate([5, 6, 7, 0, 1, 2, 4])
        0
    """
    low = 0
    high = len(array) - 1
    while low < high:
        mid = (low + high) // 2
        if array[mid] > array[high]:
            low = mid + 1
        else:
            high = mid
    return array[low]


def find_min_rotate_recur(array: list[int], low: int, high: int) -> int:
    """Find the minimum element in a rotated sorted array (recursive).

    Args:
        array: A sorted list of unique integers that has been rotated.
        low: Lower bound index of the current search range.
        high: Upper bound index of the current search range.

    Returns:
        The minimum value in the array.

    Examples:
        >>> find_min_rotate_recur([4, 5, 6, 7, 0, 1, 2], 0, 6)
        0
    """
    mid = (low + high) // 2
    if mid == low:
        return array[low]
    if array[mid] > array[high]:
        return find_min_rotate_recur(array, mid + 1, high)
    return find_min_rotate_recur(array, low, mid)
