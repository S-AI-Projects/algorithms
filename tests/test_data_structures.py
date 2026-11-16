"""Tests for data structures in algorithms/data_structures."""

import unittest

from algorithms.data_structures.avl_tree import AvlTree
from algorithms.data_structures.b_tree import BTree, Node
from algorithms.data_structures.hash_table import HashTable, ResizableHashTable
from algorithms.data_structures.red_black_tree import RBNode, RBTree
from algorithms.data_structures.segment_tree import SegmentTree
from algorithms.data_structures.separate_chaining_hash_table import (
    SeparateChainingHashTable,
)
from algorithms.data_structures.trie import Trie
from algorithms.data_structures.union_find import Union


class TestRBTree(unittest.TestCase):
    def _make_tree(self, values):
        tree = RBTree()
        for v in values:
            tree.insert(RBNode(v, 1))
        return tree

    def test_insert_single(self):
        tree = self._make_tree([5])
        result = tree.inorder()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["val"], 5)

    def test_insert_multiple_sorted(self):
        values = [11, 2, 14, 1, 7, 15, 5, 8, 4]
        tree = self._make_tree(values)
        result = tree.inorder()
        vals = [r["val"] for r in result]
        self.assertEqual(vals, sorted(values))

    def test_root_is_black(self):
        tree = self._make_tree([10, 5, 15])
        self.assertEqual(tree.root.color, 0)

    def test_empty_tree(self):
        tree = RBTree()
        self.assertIsNone(tree.root)
        self.assertEqual(tree.inorder(), [])

    def test_insert_duplicates_order(self):
        tree = self._make_tree([3, 1, 2])
        result = tree.inorder()
        vals = [r["val"] for r in result]
        self.assertEqual(vals, [1, 2, 3])


class TestAvlTree(unittest.TestCase):
    def test_insert_single(self):
        tree = AvlTree()
        tree.insert(10)
        self.assertIsNotNone(tree.node)
        self.assertEqual(tree.node.val, 10)

    def test_insert_multiple_root_exists(self):
        tree = AvlTree()
        for v in [5, 3, 7, 1, 4]:
            tree.insert(v)
        self.assertIsNotNone(tree.node)

    def test_balanced_after_insert(self):
        tree = AvlTree()
        for v in [1, 2, 3, 4, 5]:
            tree.insert(v)
        # Tree should remain balanced; height should be <= log2(5)+1 ~ 3
        self.assertLessEqual(tree.height, 3)

    def test_empty_tree(self):
        tree = AvlTree()
        self.assertIsNone(tree.node)
        self.assertEqual(tree.in_order_traverse(), [])

    def test_in_order_traverse_populated(self):
        tree = AvlTree()
        for v in [5, 3, 7, 1, 4]:
            tree.insert(v)
        self.assertEqual(tree.in_order_traverse(), [1, 3, 4, 5, 7])

    def test_insert_balance_factor(self):
        tree = AvlTree()
        for v in [5, 4, 3, 2, 1]:
            tree.insert(v)
        # After balancing, the balance factor should be within [-1, 1]
        self.assertIn(tree.balance, [-1, 0, 1])


class TestTrie(unittest.TestCase):
    def test_insert_and_search(self):
        trie = Trie()
        trie.insert("apple")
        self.assertTrue(trie.search("apple"))

    def test_search_missing(self):
        trie = Trie()
        trie.insert("apple")
        self.assertFalse(trie.search("app"))

    def test_starts_with(self):
        trie = Trie()
        trie.insert("apple")
        self.assertTrue(trie.starts_with("app"))
        self.assertFalse(trie.starts_with("apl"))

    def test_empty_trie(self):
        trie = Trie()
        self.assertFalse(trie.search("anything"))
        self.assertFalse(trie.starts_with("a"))

    def test_multiple_words(self):
        trie = Trie()
        for w in ["cat", "car", "card", "care"]:
            trie.insert(w)
        self.assertTrue(trie.search("card"))
        self.assertFalse(trie.search("ca"))
        self.assertTrue(trie.starts_with("ca"))

    def test_insert_single_char(self):
        trie = Trie()
        trie.insert("a")
        self.assertTrue(trie.search("a"))
        self.assertFalse(trie.search("b"))


class TestUnionFind(unittest.TestCase):
    def test_add_and_root(self):
        uf = Union()
        uf.add(1)
        self.assertEqual(uf.root(1), 1)

    def test_unite_connects(self):
        uf = Union()
        uf.add(1)
        uf.add(2)
        uf.unite(1, 2)
        self.assertEqual(uf.root(1), uf.root(2))

    def test_not_connected(self):
        uf = Union()
        uf.add(1)
        uf.add(2)
        self.assertNotEqual(uf.root(1), uf.root(2))

    def test_count_decrements_on_unite(self):
        uf = Union()
        uf.add(1)
        uf.add(2)
        uf.add(3)
        self.assertEqual(uf.count, 3)
        uf.unite(1, 2)
        self.assertEqual(uf.count, 2)

    def test_unite_same_element(self):
        uf = Union()
        uf.add(1)
        uf.unite(1, 1)
        self.assertEqual(uf.count, 1)

    def test_transitive_connectivity(self):
        uf = Union()
        for x in [1, 2, 3]:
            uf.add(x)
        uf.unite(1, 2)
        uf.unite(2, 3)
        self.assertEqual(uf.root(1), uf.root(3))


class TestSegmentTree(unittest.TestCase):
    def test_max_query(self):
        tree = SegmentTree([2, 4, 5, 3, 4], max)
        self.assertEqual(tree.query(2, 4), 5)

    def test_sum_query(self):
        tree = SegmentTree([1, 2, 3, 4, 5], lambda a, b: a + b)
        self.assertEqual(tree.query(0, 4), 15)

    def test_single_element_query(self):
        tree = SegmentTree([7, 2, 9], max)
        self.assertEqual(tree.query(0, 0), 7)
        self.assertEqual(tree.query(2, 2), 9)

    def test_full_range_max(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        tree = SegmentTree(arr, max)
        self.assertEqual(tree.query(0, len(arr) - 1), 9)


class TestHashTable(unittest.TestCase):
    def test_put_and_get(self):
        ht = HashTable()
        ht.put(1, "one")
        self.assertEqual(ht.get(1), "one")

    def test_get_missing(self):
        ht = HashTable()
        self.assertIsNone(ht.get(99))

    def test_delete(self):
        ht = HashTable()
        ht.put(1, "one")
        ht.del_(1)
        self.assertIsNone(ht.get(1))

    def test_update_existing(self):
        ht = HashTable()
        ht.put(1, "one")
        ht.put(1, "ONE")
        self.assertEqual(ht.get(1), "ONE")

    def test_len(self):
        ht = HashTable()
        ht.put(1, "a")
        ht.put(2, "b")
        self.assertEqual(len(ht), 2)

    def test_bracket_operators(self):
        ht = HashTable()
        ht[5] = "five"
        self.assertEqual(ht[5], "five")
        del ht[5]
        self.assertIsNone(ht[5])


class TestResizableHashTable(unittest.TestCase):
    def test_put_and_get(self):
        ht = ResizableHashTable()
        ht.put(1, "a")
        self.assertEqual(ht.get(1), "a")

    def test_resizes_automatically(self):
        ht = ResizableHashTable()
        for i in range(20):
            ht.put(i, str(i))
        for i in range(20):
            self.assertEqual(ht.get(i), str(i))


class TestSeparateChainingHashTable(unittest.TestCase):
    def test_put_and_get(self):
        table = SeparateChainingHashTable()
        table.put("hello", "world")
        self.assertEqual(table.get("hello"), "world")

    def test_get_missing(self):
        table = SeparateChainingHashTable()
        self.assertIsNone(table.get("missing"))

    def test_delete(self):
        table = SeparateChainingHashTable()
        table.put("key", "value")
        table.del_("key")
        self.assertIsNone(table.get("key"))

    def test_len(self):
        table = SeparateChainingHashTable()
        table.put("a", 1)
        table.put("b", 2)
        self.assertEqual(len(table), 2)

    def test_collision_handling(self):
        # Force collision by using small table
        table = SeparateChainingHashTable(size=1)
        table.put("x", 10)
        table.put("y", 20)
        self.assertEqual(table.get("x"), 10)
        self.assertEqual(table.get("y"), 20)

    def test_bracket_operators(self):
        table = SeparateChainingHashTable()
        table["k"] = "v"
        self.assertEqual(table["k"], "v")
        del table["k"]
        self.assertIsNone(table["k"])


if __name__ == "__main__":
    unittest.main()


class TestNodeFixture(unittest.TestCase):
    """State-isolation and fixture regression tests for Node and BTree (R24-T035).

    Fixture anchors (from docstring):
        >>> node = Node()
        >>> node.keys      # []
        >>> bt = BTree(2)

    Observable dependencies: none — Node is a pure data container with no
    network, I/O, randomness or time dependencies.
    """

    # ------------------------------------------------------------------
    # Fixture anchor: node = Node() / node.keys
    # ------------------------------------------------------------------

    def test_node_default_keys_empty(self):
        """node.keys is [] immediately after construction (docstring anchor)."""
        node = Node()
        self.assertEqual(node.keys, [])

    def test_node_default_children_empty(self):
        """node.children is [] immediately after construction."""
        node = Node()
        self.assertEqual(node.children, [])

    def test_node_is_leaf_on_creation(self):
        """A freshly created Node with no children is a leaf."""
        node = Node()
        self.assertTrue(node.is_leaf)

    def test_node_repr(self):
        """__repr__ includes the keys list."""
        node = Node()
        self.assertIn("[]", repr(node))

    # ------------------------------------------------------------------
    # Neighbouring supported input: Node with keys pre-populated
    # ------------------------------------------------------------------

    def test_node_manual_key_assignment(self):
        """Keys assigned manually are reflected immediately; is_leaf still True."""
        node = Node()
        node.keys = [10, 20]
        self.assertEqual(node.keys, [10, 20])
        self.assertTrue(node.is_leaf)

    def test_node_add_child_makes_non_leaf(self):
        """Adding a child node changes is_leaf to False."""
        parent = Node()
        child = Node()
        parent.children.append(child)
        self.assertFalse(parent.is_leaf)

    # ------------------------------------------------------------------
    # Isolation: same fixture run twice gives identical results
    # ------------------------------------------------------------------

    def test_node_fixture_twice_identical(self):
        """Running the docstring fixture twice in fresh state gives equal results."""
        node_a = Node()
        result_a = (node_a.keys[:], node_a.children[:], node_a.is_leaf)

        node_b = Node()
        result_b = (node_b.keys[:], node_b.children[:], node_b.is_leaf)

        self.assertEqual(result_a, result_b)

    def test_node_mutation_does_not_affect_independent_instance(self):
        """Mutating one Node instance does not change another (no shared state)."""
        node_a = Node()
        node_b = Node()
        node_a.keys.append(99)
        self.assertEqual(node_b.keys, [],
                         "Mutating node_a.keys leaked into node_b — shared state detected")

    def test_node_fixture_after_other_valid_input_unchanged(self):
        """Running the fixture after inserting into a BTree does not alter fresh Node."""
        # earlier operation
        bt = BTree(2)
        bt.insert_key(42)

        # fresh fixture must be unaffected
        node = Node()
        self.assertEqual(node.keys, [])
        self.assertEqual(node.children, [])

    # ------------------------------------------------------------------
    # BTree(2) fixture anchor
    # ------------------------------------------------------------------

    def test_btree_initial_state(self):
        """BTree(2) has an empty root node and correct min/max key counts."""
        bt = BTree(2)
        self.assertEqual(bt.root.keys, [])
        self.assertEqual(bt.min_numbers_of_keys, 1)   # t-1 = 1
        self.assertEqual(bt.max_number_of_keys, 3)    # 2t-1 = 3

    def test_btree_fixture_twice_identical(self):
        """BTree(2) constructed twice yields identical initial structure."""
        bt1 = BTree(2)
        bt2 = BTree(2)
        self.assertEqual(bt1.root.keys, bt2.root.keys)
        self.assertEqual(bt1.min_numbers_of_keys, bt2.min_numbers_of_keys)
        self.assertEqual(bt1.max_number_of_keys, bt2.max_number_of_keys)

    def test_btree_root_is_leaf_initially(self):
        """BTree(2) root starts as a leaf."""
        bt = BTree(2)
        self.assertTrue(bt.root.is_leaf)

    # ------------------------------------------------------------------
    # BTree insert + find (neighbouring supported inputs)
    # ------------------------------------------------------------------

    def test_btree_insert_and_find(self):
        """Inserted key is found; non-inserted key is not found."""
        bt = BTree(2)
        bt.insert_key(10)
        self.assertTrue(bt.find(10))
        self.assertFalse(bt.find(99))

    def test_btree_traverse_sorted(self):
        """traverse_tree returns keys in sorted ascending order."""
        bt = BTree(2)
        for k in [3, 1, 2]:
            bt.insert_key(k)
        self.assertEqual(bt.traverse_tree(), [1, 2, 3])

    def test_btree_remove_key(self):
        """Removed key is no longer found; other keys remain."""
        bt = BTree(2)
        for k in [5, 3, 7]:
            bt.insert_key(k)
        bt.remove_key(3)
        self.assertFalse(bt.find(3))
        self.assertTrue(bt.find(5))
        self.assertTrue(bt.find(7))

    def test_btree_independent_instances(self):
        """Two BTree instances share no state; inserting into one does not affect other."""
        bt1 = BTree(2)
        bt2 = BTree(2)
        bt1.insert_key(55)
        self.assertFalse(bt2.find(55),
                         "bt2 found 55 that was only inserted into bt1 — shared state")

    # ------------------------------------------------------------------
    # Enumeration: 20+ valid Node / BTree inputs
    # ------------------------------------------------------------------

    def test_btree_many_inserts_traverse(self):
        """Insert 20 valid keys and verify traverse_tree returns all in sorted order."""
        keys = [15, 3, 9, 7, 2, 18, 11, 5, 14, 1,
                20, 6, 13, 4, 17, 8, 12, 19, 16, 10]
        bt = BTree(2)
        for k in keys:
            bt.insert_key(k)
        self.assertEqual(bt.traverse_tree(), sorted(keys))

    def test_node_children_isolation(self):
        """child.keys mutation does not propagate to parent.keys."""
        parent = Node()
        child = Node()
        child.keys = [1, 2, 3]
        parent.children.append(child)
        child.keys.append(4)
        # parent's own keys list is unaffected
        self.assertEqual(parent.keys, [])
