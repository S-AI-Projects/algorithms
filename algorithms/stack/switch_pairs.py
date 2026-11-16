"""
Switch Pairs

Switch successive pairs of values in a stack starting from the bottom.
If there is an odd number of values, the top element is not moved.
Two approaches: one using an auxiliary stack, one using an auxiliary queue.

Reference: https://en.wikipedia.org/wiki/Stack_(abstract_data_type)

Complexity:
    Time:  O(n)
    Space: O(n)
"""

from __future__ import annotations

import collections


def first_switch_pairs(stack: list[int]) -> list[int]:
    """Switch successive pairs using an auxiliary stack.

    Contract:
        ``stack`` is read bottom to top: index 0 is the bottom and the last
        item is the top. Successive pairs are swapped starting from the
        bottom; with an odd number of values the top value is not moved.

        Supported boundaries:
            - ``[]`` -> ``[]``: an empty stack is returned empty, no error.
            - ``[a]`` -> ``[a]``: a single value has no partner and stays.
            - ``[a, b]`` -> ``[b, a]``: the smallest even stack, one swap.
            - ``[a, b, c]`` -> ``[b, a, c]``: odd count, the top value stays.

        Values are only moved, never compared, so their type does not
        affect the result.

        Mutation: ``stack`` itself is rearranged in place and that same list
        object is returned.

        Unsupported: arguments that are not lists (for example a tuple or
        ``None``). There is no guard for these, so their behaviour is
        undefined.

    Args:
        stack: A list representing a stack (bottom to top).

    Returns:
        The stack with successive pairs swapped.

    Examples:
        >>> first_switch_pairs([3, 8, 17, 9, 1, 10])
        [8, 3, 9, 17, 10, 1]
        >>> first_switch_pairs([3, 8, 17, 9, 1])
        [8, 3, 9, 17, 1]
        >>> first_switch_pairs([])
        []
    """
    storage_stack: list[int] = []
    for _ in range(len(stack)):
        storage_stack.append(stack.pop())
    for _ in range((len(storage_stack)+1)//2):
        first = storage_stack.pop()
        if len(storage_stack) == 0:
            stack.append(first)
            break
        second = storage_stack.pop()
        stack.append(second)
        stack.append(first)
    return stack


def second_switch_pairs(stack: list[int]) -> list[int]:
    """Switch successive pairs using an auxiliary queue.

    Args:
        stack: A list representing a stack (bottom to top).

    Returns:
        The stack with successive pairs swapped.

    Examples:
        >>> second_switch_pairs([3, 8, 17, 9, 1, 10])
        [8, 3, 9, 17, 10, 1]
    """
    queue: collections.deque[int] = collections.deque()
    for _ in range(len(stack)):
        queue.append(stack.pop())
    for _ in range(len(queue)):
        stack.append(queue.pop())
    for _ in range(len(stack)):
        queue.append(stack.pop())
    for _ in range(len(queue)):
        if len(queue) == 0:
            break
        first = queue.pop()
        if len(queue) == 0:
            stack.append(first)
            break
        second = queue.pop()
        stack.append(second)
        stack.append(first)

    return stack
