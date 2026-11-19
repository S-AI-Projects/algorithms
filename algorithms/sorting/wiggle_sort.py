"""
Wiggle Sort

Given an unsorted array, reorder it in-place such that
nums[0] < nums[1] > nums[2] < nums[3] ...

Reference: https://leetcode.com/problems/wiggle-sort/

Complexity:
    Time:  O(n) best / O(n) average / O(n) worst
    Space: O(1)
"""

from __future__ import annotations


def wiggle_sort(array: list[int]) -> list[int]:
    """Reorder *array* in-place into wiggle-sorted order.

    Invariant & Contract:
        - In-place mutation: `array` is modified in-place and the same list
          instance is returned (`result is array`).
        - Multiplicity preservation: The output is a permutation of `array`,
          preserving all element counts (`Counter(result) == Counter(array)`).
        - Wiggle Invariant:
            For all indices 0 <= i < len(array) - 1:
                - If i is even: array[i] <= array[i + 1]
                - If i is odd:  array[i] >= array[i + 1]
            Equivalently: nums[0] <= nums[1] >= nums[2] <= nums[3] >= ...
        - Boundaries:
            - Empty list `[]` and single-element list `[x]` trivially satisfy
              the invariant.

    Args:
        array: List of integers to reorder.

    Returns:
        The wiggle-sorted list.

    Examples:
        >>> wiggle_sort([3, 5, 2, 1, 6, 4])
        [3, 5, 1, 6, 2, 4]
        >>> wiggle_sort([3, 1, 2])
        [1, 3, 2]
        >>> wiggle_sort([2, 2, 1])
        [1, 2, 2]
        >>> wiggle_sort([])
        []
    """
    for i in range(len(array)):
        if (i % 2 == 1) == (array[i - 1] > array[i]):
            array[i - 1], array[i] = array[i], array[i - 1]
    return array
