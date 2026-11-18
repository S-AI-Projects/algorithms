"""
Cocktail Shaker Sort

Cocktail shaker sort is a variation of bubble sort that traverses the
list alternately from left-to-right and right-to-left.

Reference: https://en.wikipedia.org/wiki/Cocktail_shaker_sort

Complexity:
    Time:  O(n) best / O(n^2) average / O(n^2) worst
    Space: O(1)
"""

from __future__ import annotations


def cocktail_shaker_sort(array: list[int]) -> list[int]:
    """Sort an array in ascending order using cocktail shaker sort.

    Contract & Invariants:
        - In-place mutation: Rearranges `array` in place and returns the identical list instance.
        - Ascending ordering: Guarantees `array[i] <= array[i + 1]` for all adjacent indices.
        - Element conservation: Exactly preserves all element values and multiplicities.
        - Protected condition: Full traversal over `range(1, n)` on the forward pass and
          `range(n - 1, 0, -1)` on the reverse pass ensures arrays with tail inversions
          (e.g., `[1, 3, 2]`) are not prematurely declared sorted.

    Args:
        array: List of integers to sort.

    Returns:
        The sorted list (same instance modified in-place).

    Examples:
        >>> cocktail_shaker_sort([3, 1, 2])
        [1, 2, 3]
        >>> cocktail_shaker_sort([2, 2, 1])
        [1, 2, 2]
        >>> cocktail_shaker_sort([1, 2, 3])
        [1, 2, 3]
        >>> cocktail_shaker_sort([3, 2, 1])
        [1, 2, 3]
        >>> cocktail_shaker_sort([])
        []
    """
    n = len(array)
    swapped = True
    while swapped:
        swapped = False
        for i in range(1, n):
            if array[i - 1] > array[i]:
                array[i - 1], array[i] = array[i], array[i - 1]
                swapped = True
        if not swapped:
            return array
        swapped = False
        for i in range(n - 1, 0, -1):
            if array[i - 1] > array[i]:
                array[i - 1], array[i] = array[i], array[i - 1]
                swapped = True
    return array
