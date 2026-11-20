"""
Given a binary search tree (BST),
find the lowest common ancestor (LCA) of two given nodes in the BST.

According to the definition of LCA on Wikipedia:
    “The lowest common ancestor is defined between two
    nodes v and w as the lowest node in T that has both v and w
    as descendants (where we allow a node to be a descendant of itself).”

        _______6______
       /              \
    ___2__          ___8__
   /      \\        /      \
   0      _4       7       9
         /  \
         3   5

For example, the lowest common ancestor (LCA) of nodes 2 and 8 is 6.
Another example is LCA of nodes 2 and 4 is 2,
since a node can be a descendant of itself according to the LCA definition.
"""


def lowest_common_ancestor(root, p, q):
    """Return the lowest common ancestor of p and q in a BST.

    The LCA is the first node on the search path from the root whose key
    lies in the target range ``[min(p.val, q.val), max(p.val, q.val)]``:
    above it both keys are on the same side, and at it they split (or one
    of them is the node itself).

    Contract:
        ``root`` is the root of a binary search tree of ``TreeNode`` (or
        ``None``), and ``p`` and ``q`` are nodes of that tree. The argument
        order does not matter. The tree is only read, never modified.
        Returns the LCA node itself, or ``None`` when ``root`` is ``None``.
        Membership of ``p`` and ``q`` is not checked.

    :type root: TreeNode
    :type p: TreeNode
    :type q: TreeNode
    :rtype: TreeNode

    Examples:
        >>> from algorithms.common import TreeNode
        >>> one, three = TreeNode(1), TreeNode(3)
        >>> root = TreeNode(2, one, three)
        >>> lowest_common_ancestor(root, one, three).val
        2
        >>> lowest_common_ancestor(root, one, one) is one
        True
    """
    if not root:
        return None
    low, high = min(p.val, q.val), max(p.val, q.val)
    while root:
        if root.val < low:  # both keys are larger: go right
            root = root.right
        elif root.val > high:  # both keys are smaller: go left
            root = root.left
        else:  # low <= root.val <= high: the keys split here
            return root
