"""
Copy List with Random Pointer

Given a linked list where each node contains an additional random pointer that
could point to any node in the list or null, return a deep copy of the list.

Reference: https://leetcode.com/problems/copy-list-with-random-pointer/

Complexity:
    Time:  O(n)
    Space: O(n)
"""

from __future__ import annotations

from collections import defaultdict


class RandomListNode:
    """Node with next and random pointers for deep-copy problem.

    Contract & Supported Boundaries:
        - Attributes:
            - `label`: Value stored in the node (annotated as ``int``, but supports
              any label value such as strings).
            - `next`: Reference to the next ``RandomListNode`` in the sequence,
              or ``None`` if it is the terminal node. Initialized to ``None``.
            - `random`: Reference to an arbitrary ``RandomListNode`` in the list,
              or ``None``. Can point to itself (self-referential), an earlier node,
              a later node, or ``None``. Initialized to ``None``.
        - Identity:
            Uses standard object identity (no custom ``__eq__`` or ``__hash__``),
            allowing instances to serve directly as unique keys in dictionaries
            and sets during list traversal and deep copying.
        - Boundaries:
            - Smallest list is represented by ``None`` (empty list).
            - Smallest non-empty list contains a single ``RandomListNode``.
            - Supports falsy labels (e.g., ``0``, ``""``) without loss.
            - Calling without arguments raises ``TypeError``.
    """

    def __init__(self, label: int) -> None:
        self.label = label
        self.next: RandomListNode | None = None
        self.random: RandomListNode | None = None


def copy_random_pointer_v1(head: RandomListNode | None) -> RandomListNode | None:
    """Deep-copy a linked list with random pointers using a dictionary.

    Contract & Supported Boundaries:
        - Input: Head node of a list of ``RandomListNode``, or ``None``.
        - Output: Head of a new deep-copied list, or ``None`` if ``head`` is ``None``.
        - Boundaries:
            - Smallest list is ``None``; returns ``None`` without error.
            - Single node list (e.g., ``RandomListNode(1)`` with ``next=None``).
            - Self-referential random pointer (``node.random = node``).
            - Falsy label values (e.g., ``label = 0``) are preserved without loss.
            - Mutates neither the original nodes nor their pointers.

    Args:
        head: Head of the original list.

    Returns:
        Head of the deep-copied list.

    Examples:
        >>> node = RandomListNode(1)
        >>> node.random = node
        >>> copied = copy_random_pointer_v1(node)
        >>> copied.label == 1 and copied.random is copied
        True
        >>> copy_random_pointer_v1(None) is None
        True
    """
    node_map: dict[RandomListNode, RandomListNode] = {}
    current = head
    while current:
        node_map[current] = RandomListNode(current.label)
        current = current.next
    current = head
    while current:
        node_map[current].next = node_map.get(current.next)
        node_map[current].random = node_map.get(current.random)
        current = current.next
    return node_map.get(head)


def copy_random_pointer_v2(head: RandomListNode | None) -> RandomListNode | None:
    """Deep-copy a linked list with random pointers using defaultdict.

    Contract & Supported Boundaries:
        - Input: Head node of a list of ``RandomListNode``, or ``None``.
        - Output: Head of a new deep-copied list, or ``None`` if ``head`` is ``None``.
        - Boundaries:
            - Smallest list is ``None``; returns ``None`` without error.
            - Single node list (e.g., ``RandomListNode(1)`` with ``next=None``).
            - Self-referential random pointer (``node.random = node``).
            - Falsy label values (e.g., ``label = 0``) are preserved without loss.
            - Mutates neither the original nodes nor their pointers.

    Args:
        head: Head of the original list.

    Returns:
        Head of the deep-copied list.

    Examples:
        >>> node = RandomListNode(1)
        >>> node.random = node
        >>> copied = copy_random_pointer_v2(node)
        >>> copied.label == 1 and copied.random is copied
        True
        >>> copy_random_pointer_v2(None) is None
        True
    """
    copy: defaultdict[RandomListNode | None, RandomListNode | None] = defaultdict(
        lambda: RandomListNode(0)
    )
    copy[None] = None
    node = head
    while node:
        copy[node].label = node.label
        copy[node].next = copy[node.next]
        copy[node].random = copy[node.random]
        node = node.next
    return copy[head]
