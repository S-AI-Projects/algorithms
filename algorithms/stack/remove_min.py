"""
Remove Min from Stack

Remove the smallest value from a stack, preserving the relative order
of the remaining elements.

Reference: https://en.wikipedia.org/wiki/Stack_(abstract_data_type)

Complexity:
    Time:  O(n)
    Space: O(n)
"""

from __future__ import annotations


def remove_min(stack: list[int]) -> list[int]:
    """Remove the minimum value from the stack.

    Contract:
        ``stack`` is read bottom to top (index 0 is the bottom). Every copy
        of the smallest value is removed and the other values keep their
        order. An empty stack is returned unchanged. The list passed in is
        modified in place and that same list is returned.

    Dependencies:
        None. The function only works on the list it is given, using
        ``len``, ``range`` and the list's ``pop`` and ``append``. It reads
        no global state, files, network, clock or random numbers, so the
        same values always give the same result and an earlier call cannot
        change a later one.

    Args:
        stack: A list representing a stack (bottom to top).

    Returns:
        The stack with the minimum value removed.

    Examples:
        >>> remove_min([2, 8, 3, -6, 7, 3])
        [2, 8, 3, 7, 3]
        >>> remove_min([4, 8, 3, 7, 3])
        [4, 8, 7]
        >>> remove_min([])
        []
    """
    storage_stack: list[int] = []
    if len(stack) == 0:
        return stack
    minimum = stack.pop()
    stack.append(minimum)
    for _ in range(len(stack)):
        val = stack.pop()
        if val <= minimum:
            minimum = val
        storage_stack.append(val)
    for _ in range(len(storage_stack)):
        val = storage_stack.pop()
        if val != minimum:
            stack.append(val)
    return stack
