"""Imports TreeNodes"""

from __future__ import annotations

from algorithms.common.tree_node import TreeNode


class AvlTree:
    """
    An AVL tree implementation supporting balanced binary search tree operations.

    Invariants:
        - For every node, balance factor = height(left) - height(right) is in {-1, 0, 1}.
        - Rebalancing uses left and right rotations to maintain O(log n) height.
        - in_order_traverse returns keys in sorted ascending order.
    """

    def __init__(self):
        # Root node of the tree.
        self.node = None
        self.height = -1
        self.balance = 0

    def insert(self, key):
        """
        Insert new key into node
        """
        # Create new node
        node = TreeNode(key)
        if not self.node:
            self.node = node
            self.node.left = AvlTree()
            self.node.right = AvlTree()
        elif key < self.node.val:
            self.node.left.insert(key)
        elif key > self.node.val:
            self.node.right.insert(key)
        self.re_balance()

    def _refresh_metrics(self):
        """Update both heights and balance factors for this subtree."""
        self.update_heights()
        self.update_balances()

    def re_balance(self):
        """
        Re balance tree. After inserting or deleting a node,
        """
        self.update_heights(recursive=False)
        self.update_balances(False)

        while abs(self.balance) > 1:
            if self.balance > 1:
                if self.node.left.balance < 0:
                    self.node.left.rotate_left()
                    self._refresh_metrics()
                self.rotate_right()
                self._refresh_metrics()

            if self.balance < -1:
                if self.node.right.balance > 0:
                    self.node.right.rotate_right()
                    self._refresh_metrics()
                self.rotate_left()
                self._refresh_metrics()

    def update_heights(self, recursive=True):
        """
        Update tree height
        """
        if self.node:
            if recursive:
                if self.node.left:
                    self.node.left.update_heights()
                if self.node.right:
                    self.node.right.update_heights()

            self.height = 1 + max(self.node.left.height, self.node.right.height)
        else:
            self.height = -1

    def update_balances(self, recursive=True):
        """
        Calculate tree balance factor

        """
        if self.node:
            if recursive:
                if self.node.left:
                    self.node.left.update_balances()
                if self.node.right:
                    self.node.right.update_balances()

            self.balance = self.node.left.height - self.node.right.height
        else:
            self.balance = 0

    def rotate_right(self):
        """
        Right rotation
        """
        new_root = self.node.left.node
        new_left_sub = new_root.right.node
        old_root = self.node

        self.node = new_root
        old_root.left.node = new_left_sub
        new_root.right.node = old_root

    def rotate_left(self):
        """
        Left rotation
        """
        new_root = self.node.right.node
        new_left_sub = new_root.left.node
        old_root = self.node

        self.node = new_root
        old_root.right.node = new_left_sub
        new_root.left.node = old_root

    def in_order_traverse(self):
        """
        In-order traversal of the tree.

        Returns:
            List of node values in sorted ascending order.

        Examples:
            >>> tree = AvlTree()
            >>> tree.in_order_traverse()
            []
            >>> for val in [5, 3, 7, 1, 4]:
            ...     tree.insert(val)
            >>> tree.in_order_traverse()
            [1, 3, 4, 5, 7]
        """
        result = []

        if not self.node:
            return result

        result.extend(self.node.left.in_order_traverse())
        result.append(self.node.val)
        result.extend(self.node.right.in_order_traverse())
        return result
