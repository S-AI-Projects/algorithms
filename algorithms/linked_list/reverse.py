"""
Reverse Linked List

Reverse a singly linked list. Both iterative and recursive solutions are
provided.

Reference: https://leetcode.com/problems/reverse-linked-list/

Complexity:
    Time:  O(n)
    Space: O(1) iterative, O(n) recursive
"""

from __future__ import annotations


def reverse_list(head: object | None) -> object | None:
    """Reverse a singly linked list iteratively.

    Args:
        head: Head node of the linked list (must have .next attr).

    Returns:
        The new head of the reversed list.

    Supported input:
        ``None`` (the empty list) or the head of a finite, acyclic list of
        truthy nodes such as ``ListNode``. The loop stops at the first falsy
        ``next``, so cyclic lists are not supported.

    Invariant:
        If the input is nodes ``n0 -> n1 -> ... -> nk``, the result is the
        same node objects linked ``nk -> ... -> n1 -> n0``, ending in
        ``None``. Every input node appears exactly once, no node is created
        or copied, and no ``val`` is changed. Only the ``next`` links move.

    Mutation:
        The list is reversed in place. After the call, the caller's old
        ``head`` is the tail of the result (its ``next`` is ``None``), so it
        no longer reaches the other nodes. Use the returned head. An empty
        or single-node list is returned unchanged.

    Examples:
        >>> reverse_list(None) is None
        True
        >>> from algorithms.common import ListNode
        >>> a, b, c = ListNode(1), ListNode(2), ListNode(3)
        >>> a.next, b.next = b, c
        >>> new_head = reverse_list(a)
        >>> new_head is c and c.next is b and b.next is a and a.next is None
        True
    """
    if not head or not head.next:
        return head
    prev = None
    while head:
        current = head
        head = head.next
        current.next = prev
        prev = current
    return prev


def reverse_list_recursive(head: object | None) -> object | None:
    """Reverse a singly linked list recursively.

    Args:
        head: Head node of the linked list (must have .next attr).

    Returns:
        The new head of the reversed list.

    Examples:
        >>> reverse_list_recursive(None) is None
        True
    """
    if head is None or head.next is None:
        return head
    rest = head.next
    head.next = None
    reversed_rest = reverse_list_recursive(rest)
    rest.next = head
    return reversed_rest
