"""
Pancake Sort

Pancake sort sorts an array by repeatedly finding the maximum element in
the unsorted portion, flipping it to the front, and then flipping the
entire unsorted portion so the maximum lands at the end.

Reference: https://en.wikipedia.org/wiki/Pancake_sorting

Complexity:
    Time:  O(n) best / O(n^2) average / O(n^2) worst
    Space: O(1)
"""

from __future__ import annotations


def pancake_sort(array: list[int]) -> list[int]:
    """Sort an array in ascending order using pancake sort.

    Args:
        array: List of integers to sort.

    Returns:
        A sorted list.

    The list is sorted in place and the same list object is returned. An
    empty or one-element list is returned unchanged.

    How it works:
        Each pass handles the unsorted prefix ``array[:cur]``, for ``cur``
        from ``len(array)`` down to 2. A flip reverses a prefix. If the
        largest value of the prefix is not already at index ``cur - 1``, the
        pass flips it to the front (skipped when it is already there) and
        then flips ``array[:cur]`` so it lands at index ``cur - 1``.

        The decisive state transition: after the pass for ``cur``, the
        largest value of ``array[:cur]`` is at index ``cur - 1``, so the
        sorted suffix ``array[cur - 1:]`` grows by one and is never touched
        again. A value already in place costs no flips.

    Worked example, the state after each flip:
        ``[1, 3, 2]``: cur=3, max 3 at index 1, flip ``[:2]`` -> ``[3, 1, 2]``,
        then flip ``[:3]`` -> ``[2, 1, 3]`` (3 is final); cur=2, max 2 at
        index 0, flip ``[:2]`` -> ``[1, 2, 3]``.

        ``[3, 1, 2]``: cur=3, max 3 already at the front, so only
        ``[:3]`` is flipped -> ``[2, 1, 3]``; cur=2, flip ``[:2]`` ->
        ``[1, 2, 3]``.

        ``[2, 2, 1]``: cur=3, the first 2 is at the front, flip ``[:3]``
        -> ``[1, 2, 2]``; cur=2, 2 is already at index 1, no flip.

        ``[1, 2, 3]`` needs no flips, and ``[3, 2, 1]`` needs one flip of
        ``[:3]``.

    Examples:
        >>> pancake_sort([3, 1, 2])
        [1, 2, 3]
        >>> pancake_sort([1, 3, 2])
        [1, 2, 3]
        >>> pancake_sort([2, 2, 1])
        [1, 2, 2]
        >>> pancake_sort([1, 2, 3])
        [1, 2, 3]
        >>> pancake_sort([3, 2, 1])
        [1, 2, 3]
        >>> pancake_sort([])
        []
        >>> pancake_sort([5])
        [5]
        >>> data = [3, 1, 2]
        >>> pancake_sort(data) is data
        True
        >>> data
        [1, 2, 3]
    """
    if len(array) <= 1:
        return array

    for cur in range(len(array), 1, -1):
        index_max = array.index(max(array[0:cur]))
        if index_max + 1 != cur:
            if index_max != 0:
                array[: index_max + 1] = reversed(array[: index_max + 1])
            array[:cur] = reversed(array[:cur])
    return array
