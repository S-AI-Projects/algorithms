import unittest

from algorithms.common import TreeNode
from algorithms.data_structures.b_tree import BTree
from algorithms.data_structures.fenwick_tree import Fenwick_Tree
from algorithms.tree import construct_tree_postorder_preorder as ctpp
from algorithms.tree.bst_lowest_common_ancestor import lowest_common_ancestor
from algorithms.tree.traversal_inorder import inorder, inorder_rec
from algorithms.tree.traversal_postorder import postorder, postorder_rec
from algorithms.tree.traversal_preorder import preorder, preorder_rec


class Node:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class TestTraversal(unittest.TestCase):
    def test_preorder(self):
        tree = create_tree()
        self.assertEqual([100, 50, 25, 75, 150, 125, 175], preorder(tree))
        self.assertEqual([100, 50, 25, 75, 150, 125, 175], preorder_rec(tree))

    def test_postorder(self):
        tree = create_tree()
        self.assertEqual([25, 75, 50, 125, 175, 150, 100], postorder(tree))
        self.assertEqual([25, 75, 50, 125, 175, 150, 100], postorder_rec(tree))

    def test_inorder(self):
        tree = create_tree()
        self.assertEqual([25, 50, 75, 100, 125, 150, 175], inorder(tree))
        self.assertEqual([25, 50, 75, 100, 125, 150, 175], inorder_rec(tree))


def create_tree():
    n1 = Node(100)
    n2 = Node(50)
    n3 = Node(150)
    n4 = Node(25)
    n5 = Node(75)
    n6 = Node(125)
    n7 = Node(175)
    n1.left, n1.right = n2, n3
    n2.left, n2.right = n4, n5
    n3.left, n3.right = n6, n7
    return n1


class TestBTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import random

        random.seed(18719)
        cls.random = random
        cls.range = 10000

    def setUp(self):
        self.keys_to_insert = [
            self.random.randrange(-self.range, self.range) for i in range(self.range)
        ]

    def test_insertion_and_find_even_degree(self):
        btree = BTree(4)
        for i in self.keys_to_insert:
            btree.insert_key(i)

        for _ in range(100):
            key = self.random.choice(self.keys_to_insert)
            self.assertTrue(btree.find(key))

    def test_insertion_and_find_odd_degree(self):
        btree = BTree(3)
        for i in self.keys_to_insert:
            btree.insert_key(i)

        for _ in range(100):
            key = self.random.choice(self.keys_to_insert)
            self.assertTrue(btree.find(key))

    def test_deletion_even_degree(self):
        btree = BTree(4)
        key_list = set(self.keys_to_insert)
        for i in key_list:
            btree.insert_key(i)

        for key in key_list:
            btree.remove_key(key)
            self.assertFalse(btree.find(key))

        self.assertEqual(btree.root.keys, [])
        self.assertEqual(btree.root.children, [])

    def test_deletion_odd_degree(self):
        btree = BTree(3)
        key_list = set(self.keys_to_insert)
        for i in key_list:
            btree.insert_key(i)

        for key in key_list:
            btree.remove_key(key)
            self.assertFalse(btree.find(key))

        self.assertEqual(btree.root.keys, [])
        self.assertEqual(btree.root.children, [])


class TestConstructTreePreorderPostorder(unittest.TestCase):
    def test_construct_tree(self):

        # Test 1
        ctpp.pre_index = 0
        pre1 = [1, 2, 4, 8, 9, 5, 3, 6, 7]
        post1 = [8, 9, 4, 5, 2, 6, 7, 3, 1]
        size1 = len(pre1)

        self.assertEqual(
            ctpp.construct_tree(pre1, post1, size1), [8, 4, 9, 2, 5, 1, 6, 3, 7]
        )

        # Test 2
        ctpp.pre_index = 0
        pre2 = [1, 2, 4, 5, 3, 6, 7]
        post2 = [4, 5, 2, 6, 7, 3, 1]
        size2 = len(pre2)

        self.assertEqual(ctpp.construct_tree(pre2, post2, size2), [4, 2, 5, 1, 6, 3, 7])

        # Test 3
        ctpp.pre_index = 0
        pre3 = [12, 7, 16, 21, 5, 1, 9]
        post3 = [16, 21, 7, 1, 9, 5, 12]
        size3 = len(pre3)

        self.assertEqual(
            ctpp.construct_tree(pre3, post3, size3), [16, 7, 21, 12, 1, 5, 9]
        )


class TestFenwickTree(unittest.TestCase):
    def test_construct_tree_with_update_1(self):
        freq = [2, 1, 1, 3, 2, 3, 4, 5, 6, 7, 8, 9]
        ft = Fenwick_Tree(freq)
        bit_tree = ft.construct()
        self.assertEqual(12, ft.get_sum(bit_tree, 5))

        freq[3] += 6
        ft.update_bit(bit_tree, 3, 6)
        self.assertEqual(18, ft.get_sum(bit_tree, 5))

    def test_construct_tree_with_update_2(self):
        freq = [1, 2, 3, 4, 5]
        ft = Fenwick_Tree(freq)
        bit_tree = ft.construct()
        self.assertEqual(10, ft.get_sum(bit_tree, 3))

        freq[3] -= 5
        ft.update_bit(bit_tree, 3, -5)
        self.assertEqual(5, ft.get_sum(bit_tree, 3))

    def test_construct_tree_with_update_3(self):
        freq = [2, 1, 4, 6, -1, 5, -32, 0, 1]
        ft = Fenwick_Tree(freq)
        bit_tree = ft.construct()
        self.assertEqual(12, ft.get_sum(bit_tree, 4))

        freq[2] += 11
        ft.update_bit(bit_tree, 2, 11)
        self.assertEqual(23, ft.get_sum(bit_tree, 4))


def _bst_insert(root, val):
    """Insert val into the BST rooted at root and return the root."""
    if root is None:
        return TreeNode(val)
    if val < root.val:
        root.left = _bst_insert(root.left, val)
    else:
        root.right = _bst_insert(root.right, val)
    return root


def _build_fixture():
    """Keys 4, 2, 6, 1, 3, 5, 7 inserted in that order:

            4
          /   \\
         2     6
        / \\   / \\
       1   3 5   7
    """
    root = None
    for key in (4, 2, 6, 1, 3, 5, 7):
        root = _bst_insert(root, key)
    nodes = {}
    stack = [root]
    while stack:
        node = stack.pop()
        if node is not None:
            nodes[node.val] = node
            stack.extend((node.left, node.right))
    return root, nodes


def _path_to(root, node):
    """Nodes from root down to node, found by plain BST search."""
    path = [root]
    while path[-1] is not node:
        current = path[-1]
        path.append(current.left if node.val < current.val else current.right)
    return path


def _shape(node):
    """(val, id, left shape, right shape) to detect any change to the tree."""
    if node is None:
        return None
    return (node.val, id(node), _shape(node.left), _shape(node.right))


class TestBstLowestCommonAncestor(unittest.TestCase):
    """Regression tests for lowest_common_ancestor (R24-T046).

    Fixture: the BST built from keys 4, 2, 6, 1, 3, 5, 7 using TreeNode.
    The refactored step is the check of whether the current node's key lies
    in the target range [min(p, q), max(p, q)]; it is exercised at the root
    and at leaves.
    """

    def setUp(self):
        self.root, self.nodes = _build_fixture()

    def lca(self, p, q):
        return lowest_common_ancestor(self.root, self.nodes[p], self.nodes[q])

    def test_fixture_shape(self):
        n = self.nodes
        self.assertIs(self.root, n[4])
        self.assertEqual((n[4].left.val, n[4].right.val), (2, 6))
        self.assertEqual((n[2].left.val, n[2].right.val), (1, 3))
        self.assertEqual((n[6].left.val, n[6].right.val), (5, 7))

    def test_split_at_root(self):
        # 1 < 4 < 7: the root is already in range, so it is the answer.
        self.assertIs(self.lca(1, 7), self.nodes[4])
        self.assertIs(self.lca(3, 5), self.nodes[4])

    def test_root_is_one_of_the_targets(self):
        self.assertIs(self.lca(4, 1), self.nodes[4])
        self.assertIs(self.lca(6, 4), self.nodes[4])

    def test_same_leaf(self):
        # The search walks down to the leaf, whose key is the whole range.
        self.assertIs(self.lca(1, 1), self.nodes[1])
        self.assertIs(self.lca(7, 7), self.nodes[7])

    def test_two_leaves_under_one_parent(self):
        self.assertIs(self.lca(1, 3), self.nodes[2])
        self.assertIs(self.lca(5, 7), self.nodes[6])

    def test_leaf_and_its_parent(self):
        self.assertIs(self.lca(3, 2), self.nodes[2])
        self.assertIs(self.lca(6, 5), self.nodes[6])

    def test_argument_order_does_not_matter(self):
        for p, q in ((1, 3), (5, 4), (7, 2)):
            with self.subTest(p=p, q=q):
                self.assertIs(self.lca(p, q), self.lca(q, p))

    def test_all_pairs_match_path_oracle(self):
        # Independent oracle: last shared node of the two root-to-node paths.
        for p in self.nodes.values():
            for q in self.nodes.values():
                path_p = _path_to(self.root, p)
                path_q = _path_to(self.root, q)
                shared = [a for a, b in zip(path_p, path_q, strict=False) if a is b]
                with self.subTest(p=p.val, q=q.val):
                    self.assertIs(lowest_common_ancestor(self.root, p, q), shared[-1])

    def test_tree_is_not_modified(self):
        before = _shape(self.root)
        self.lca(1, 7)
        self.lca(3, 3)
        self.assertEqual(_shape(self.root), before)

    def test_empty_tree(self):
        self.assertIsNone(lowest_common_ancestor(None, TreeNode(1), TreeNode(2)))


if __name__ == "__main__":
    unittest.main()
