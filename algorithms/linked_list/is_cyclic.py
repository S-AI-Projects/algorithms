"""
Linked List Cycle Detection

Given a linked list, determine if it has a cycle using Floyd's Tortoise and
Hare algorithm without extra space.

Reference: https://leetcode.com/problems/linked-list-cycle/

Complexity:
    Time:  O(n)
    Space: O(1)
"""

from __future__ import annotations


class Node:
    """Singly linked list node.

    Structural Invariants:
        - Value preservation: `node.val` holds the assigned payload without alteration.
        - Link integrity: `node.next` points either to another `Node` instance or `None`.
        - Acyclic termination: In an acyclic chain of length n, traversal from `head`
          terminates at `None` in exactly n steps, visiting each node identity once.
        - Non-mutation contract: Inspection functions (like `is_cyclic`) must preserve
          both `.val` and `.next` references across the entire list.
    """

    def __init__(self, x: object) -> None:
        self.val = x
        self.next: Node | None = None


def is_cyclic(head: Node | None) -> bool:
    """Determine whether a linked list contains a cycle.

    Args:
        head: Head of the linked list.

    Returns:
        True if the list has a cycle, False otherwise.

    Examples:
        >>> a = Node(1); b = Node(2); a.next = b; b.next = a
        >>> is_cyclic(a)
        True
        >>> c = Node(3); c.next = Node(4)
        >>> is_cyclic(c)
        False
        >>> is_cyclic(None)
        False
    """
    if not head:
        return False
    runner = head
    walker = head
    while runner.next and runner.next.next:
        runner = runner.next.next
        walker = walker.next
        if runner == walker:
            return True
    return False
