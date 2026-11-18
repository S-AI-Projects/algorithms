"""
Subtree Check

Given two binary trees s and t, check whether t is a subtree of s. A subtree
of s is a tree consisting of a node in s and all of its descendants.

Reference: https://en.wikipedia.org/wiki/Binary_tree

Complexity:
    Time:  O(m * n) where m and n are sizes of the two trees
    Space: O(m) due to BFS queue
"""

from __future__ import annotations

import collections

from algorithms.tree.tree import TreeNode


def is_subtree(big: TreeNode, small: TreeNode) -> bool:
    """Check whether the small tree is a subtree of the big tree.

    Contract:
        - Traverses the `big` tree level-by-level using BFS.
        - When a node matching `small.val` is identified, verifies subtree equality
          via structural recursion (`_comp`).
        - Returns True immediately upon finding a valid subtree match, otherwise False.
        - Pure inspection function: does not mutate either tree.

    Args:
        big: The root of the larger tree.
        small: The root of the potential subtree.

    Returns:
        True if small is a subtree of big, False otherwise.

    Examples:
        >>> node = TreeNode(1)
        >>> is_subtree(node, node)
        True
        >>> big = TreeNode(1)
        >>> big.left = TreeNode(2); big.right = TreeNode(3)
        >>> small = TreeNode(2)
        >>> is_subtree(big, small)
        True
    """
    queue: collections.deque[TreeNode] = collections.deque([big])
    while queue:
        node = queue.popleft()
        if node.val == small.val:
            return _comp(node, small)
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
    return False


def _comp(p: TreeNode | None, q: TreeNode | None) -> bool:
    """Recursively compare two trees for structural and value equality.

    Args:
        p: A node from the first tree.
        q: A node from the second tree.

    Returns:
        True if both subtrees are identical, False otherwise.
    """
    if p is None and q is None:
        return True
    if p is not None and q is not None:
        return p.val == q.val and _comp(p.left, q.left) and _comp(p.right, q.right)
    return False
