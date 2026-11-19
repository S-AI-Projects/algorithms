"""Exponential search — locate an element in a sorted array.

First finds a range where the target may lie by doubling the index,
then performs binary search within that range. Useful when the target
is near the beginning of a large or unbounded list.

Time: O(log i) where i is the index of the target.

Inspired by PR #867 (yuviii99).
"""

from __future__ import annotations


def exponential_search(arr: list[int], target: int) -> int:
    """Return the index of *target* in sorted *arr*, or -1 if absent.

    Contract:
        - Input: `arr` is an ascending sorted list of integers; `target` is
          an integer to locate.
        - Output: Returns 0-based index `i` such that `arr[i] == target`, or
          -1 if `target` is not present in `arr`.
        - When `arr` is empty, returns -1.
        - When `target` appears multiple times, returns a valid index where
          `arr[index] == target`.
        - Non-mutation: `arr` is only inspected and never modified.

    Worked Example (Representative Result):
        Searching for `target = 8` in `arr = [2, 4, 6, 8]`:
        1. Check `arr[0]` (2 != 8).
        2. Set `bound = 1`. Since `arr[1] = 4 <= 8`, double `bound` to 2.
        3. Since `arr[2] = 6 <= 8`, double `bound` to 4.
        4. Now `bound = 4 >= len(arr)`, loop terminates.
        5. Binary search range: `low = bound // 2 = 2`, `high = min(4, 3) = 3`.
        6. Subarray `arr[2:4] = [6, 8]`: `mid = (2 + 3) // 2 = 2`.
           `arr[2] = 6 < 8`, so `low = mid + 1 = 3`.
        7. Next step: `mid = 3`, `arr[3] == 8`. Returns index 3.

    Args:
        arr: A sorted list of integers.
        target: The integer to find.

    Returns:
        The index of target in arr, or -1 if not found.

    Examples:
        >>> exponential_search([2, 4, 6, 8], 2)
        0
        >>> exponential_search([2, 4, 6, 8], 8)
        3
        >>> exponential_search([2, 4, 6, 8], 5)
        -1
        >>> exponential_search([42], 42)
        0
        >>> exponential_search([], 5)
        -1
    """
    if not arr:
        return -1
    if arr[0] == target:
        return 0
    bound = 1
    while bound < len(arr) and arr[bound] <= target:
        bound *= 2
    low = bound // 2
    high = min(bound, len(arr) - 1)
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
