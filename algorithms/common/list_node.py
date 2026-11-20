"""Singly linked list node shared across all linked list algorithms.

This module provides the universal ListNode used by every linked list
algorithm in this library. Using a single shared type means you can
compose algorithms: merge two lists, reverse the result, check if
it's a palindrome.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListNode:
    """A node in a singly linked list.

    Attributes:
        val: The value stored in this node.
        next: Reference to the next node.

    Contract (behavior comes from ``@dataclass`` with its default options):
        Construction: ``ListNode(val=0, next=None)``, positional or keyword.
            ``ListNode()`` is the smallest node: ``val == 0``, ``next is None``.
            Values are stored as given; no type checking or copying is done,
            so ``next`` is the same object that was passed in.
        End of list: ``next is None`` marks the tail. A single node is a
            one-element list.
        Truthiness: every node is truthy, including ``ListNode(0)``, so
            ``while node:`` stops only at ``None``.
        Equality: ``==`` compares ``val`` and then ``next`` recursively, so two
            lists are equal only if they have the same values in the same
            order and the same length. Comparing with a non-``ListNode``
            returns ``False``.
        Mutation: ``val`` and ``next`` can be reassigned to relink a list.
        Hashing: nodes are unhashable (``hash()`` raises ``TypeError``), so
            they cannot be put in a ``set`` or used as ``dict`` keys. Use
            ``id(node)`` when tracking visited nodes.
        Repr: ``ListNode(val=1, next=None)``; a cycle is shown as ``next=...``.

    Unsupported:
        ``val`` is typed ``int``. Other values are stored but not supported by
        the algorithms that use this type. ``==`` and ``repr`` recurse once per
        node, so very long lists (hundreds of nodes, depending on the
        interpreter's recursion limit) and ``==`` between two different cyclic
        lists can raise ``RecursionError``.

    Examples:
        >>> head = ListNode(1, ListNode(2, ListNode(3)))
        >>> head.val
        1
        >>> head.next.val
        2
        >>> ListNode()
        ListNode(val=0, next=None)
    """

    val: int = 0
    next: ListNode | None = None
