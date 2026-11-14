"""
Remove Duplicates from Linked List

Remove duplicate values from an unsorted linked list.
Two approaches:
1. Using a hash set: O(n) time, O(n) space.
2. Without a hash set: O(n^2) time, O(1) space.
"""

from __future__ import annotations


class Node:
    def __init__(self, val: object = None) -> None:
        self.val = val
        self.next: Node | None = None


def remove_dups(head: Node | None) -> None:
    """Remove duplicates using a hash set."""

    seen = set()
    prev = None
    current = head

    while current:
        if current.val in seen:
            prev.next = current.next
        else:
            seen.add(current.val)
            prev = current

        current = current.next


def remove_dups_without_set(head: Node | None) -> None:
    """Remove duplicates without using extra space."""

    current = head

    while current:
        runner = current

        while runner.next:
            if runner.next.val == current.val:
                runner.next = runner.next.next
            else:
                runner = runner.next

        current = current.next
