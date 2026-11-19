"""
Remove Range from Linked List

Given a linked list and a start and end index, remove the elements at those
indexes (inclusive) from the list.

Reference: https://en.wikipedia.org/wiki/Linked_list

Complexity:
    Time:  O(n)
    Space: O(1)
"""

from __future__ import annotations


def _advance(node: object | None, steps: int) -> object | None:
    """Advance *node* forward by *steps* links, returning None if exhausted."""
    current = node
    for _ in range(steps):
        if current is not None:
            current = current.next
        else:
            return None
    return current


def remove_range(head: object | None, start: int, end: int) -> object | None:
    """Remove nodes from index start to end (inclusive) from a linked list.

    Contract:
        - `head`: Head node of a singly linked list (must have `.next` attr) or None.
        - `start`, `end`: 0-based indices defining the range of nodes to
          remove (inclusive). Precondition: `start <= end`.
        - Returns: The head of the modified list after removing nodes in range
          [start, end].
        - Mutation: Modifies the links of the input list in-place.
        - Boundaries:
            - `head is None`: returns `None`.
            - `start == 0`: removes from the front of the list, returning a new head.

    Args:
        head: Head node of the linked list (must have .next attr).
        start: Starting index of the range to remove.
        end: Ending index of the range to remove (inclusive).

    Returns:
        The (possibly new) head of the modified list.

    Examples:
        >>> remove_range(None, 0, 0) is None
        True
    """
    assert start <= end
    if start == 0:
        head = _advance(head, end + 1)
    else:
        current = _advance(head, start - 1)
        for _ in range(end - start + 1):
            if current is not None and current.next is not None:
                current.next = current.next.next
    return head
