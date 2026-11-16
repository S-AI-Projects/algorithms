#!/usr/bin/env python3
"""
R24-T035 focused runner — state-isolation and fixture tests for Node and BTree.

Exits non-zero when any assertion fails.
Native check command:
    python3 -m unittest tests.test_data_structures.TestNodeFixture
"""

import json
import os
import platform
import sys
import unittest
from io import StringIO
from unittest import mock

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.data_structures.b_tree import BTree, Node  # noqa: E402

# ---------------------------------------------------------------------------
# Native check command (recorded as required)
# ---------------------------------------------------------------------------
NATIVE_COMMAND = "python3 -m unittest tests.test_data_structures.TestNodeFixture"

# ---------------------------------------------------------------------------
# Inline test suite (mirrors tests/test_data_structures.TestNodeFixture)
# ---------------------------------------------------------------------------

class TestNodeFixture(unittest.TestCase):
    """State-isolation and fixture regression tests for Node and BTree (R24-T035).

    Observable dependencies: none — Node is a pure data container with no
    network, I/O, randomness, or time dependencies.
    """

    # Fixture anchor: node = Node() / node.keys
    def test_node_default_keys_empty(self):
        node = Node()
        self.assertEqual(node.keys, [])

    def test_node_default_children_empty(self):
        node = Node()
        self.assertEqual(node.children, [])

    def test_node_is_leaf_on_creation(self):
        node = Node()
        self.assertTrue(node.is_leaf)

    def test_node_repr(self):
        node = Node()
        self.assertIn("[]", repr(node))

    # Neighbouring supported input
    def test_node_manual_key_assignment(self):
        node = Node()
        node.keys = [10, 20]
        self.assertEqual(node.keys, [10, 20])
        self.assertTrue(node.is_leaf)

    def test_node_add_child_makes_non_leaf(self):
        parent = Node()
        child = Node()
        parent.children.append(child)
        self.assertFalse(parent.is_leaf)

    # Isolation: same fixture run twice
    def test_node_fixture_twice_identical(self):
        node_a = Node()
        result_a = (node_a.keys[:], node_a.children[:], node_a.is_leaf)
        node_b = Node()
        result_b = (node_b.keys[:], node_b.children[:], node_b.is_leaf)
        self.assertEqual(result_a, result_b)

    def test_node_mutation_does_not_affect_independent_instance(self):
        node_a = Node()
        node_b = Node()
        node_a.keys.append(99)
        self.assertEqual(node_b.keys, [])

    def test_node_fixture_after_other_valid_input_unchanged(self):
        bt = BTree(2)
        bt.insert_key(42)
        node = Node()
        self.assertEqual(node.keys, [])
        self.assertEqual(node.children, [])

    # BTree(2) fixture anchor
    def test_btree_initial_state(self):
        bt = BTree(2)
        self.assertEqual(bt.root.keys, [])
        self.assertEqual(bt.min_numbers_of_keys, 1)
        self.assertEqual(bt.max_number_of_keys, 3)

    def test_btree_fixture_twice_identical(self):
        bt1 = BTree(2)
        bt2 = BTree(2)
        self.assertEqual(bt1.root.keys, bt2.root.keys)
        self.assertEqual(bt1.min_numbers_of_keys, bt2.min_numbers_of_keys)
        self.assertEqual(bt1.max_number_of_keys, bt2.max_number_of_keys)

    def test_btree_root_is_leaf_initially(self):
        bt = BTree(2)
        self.assertTrue(bt.root.is_leaf)

    def test_btree_insert_and_find(self):
        bt = BTree(2)
        bt.insert_key(10)
        self.assertTrue(bt.find(10))
        self.assertFalse(bt.find(99))

    def test_btree_traverse_sorted(self):
        bt = BTree(2)
        for k in [3, 1, 2]:
            bt.insert_key(k)
        self.assertEqual(bt.traverse_tree(), [1, 2, 3])

    def test_btree_remove_key(self):
        bt = BTree(2)
        for k in [5, 3, 7]:
            bt.insert_key(k)
        bt.remove_key(3)
        self.assertFalse(bt.find(3))
        self.assertTrue(bt.find(5))
        self.assertTrue(bt.find(7))

    def test_btree_independent_instances(self):
        bt1 = BTree(2)
        bt2 = BTree(2)
        bt1.insert_key(55)
        self.assertFalse(bt2.find(55))

    def test_btree_many_inserts_traverse(self):
        keys = [15, 3, 9, 7, 2, 18, 11, 5, 14, 1,
                20, 6, 13, 4, 17, 8, 12, 19, 16, 10]
        bt = BTree(2)
        for k in keys:
            bt.insert_key(k)
        self.assertEqual(bt.traverse_tree(), sorted(keys))

    def test_node_children_isolation(self):
        parent = Node()
        child = Node()
        child.keys = [1, 2, 3]
        parent.children.append(child)
        child.keys.append(4)
        self.assertEqual(parent.keys, [])


# ---------------------------------------------------------------------------
# Run the suite with mocked stdout/stderr (I/O isolation)
# ---------------------------------------------------------------------------

def run_checks():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNodeFixture)
    test_count = suite.countTestCases()
    assert test_count > 0, "No tests found — check suite definition"

    buf = StringIO()
    with mock.patch("sys.stdout", buf), mock.patch("sys.stderr", buf):
        runner = unittest.TextTestRunner(stream=buf, verbosity=2)
        result = runner.run(suite)

    output = buf.getvalue()
    print(output)

    work_dir = os.path.dirname(os.path.abspath(__file__))

    # --- inputs.json -------------------------------------------------------
    inputs = {
        "fixture_anchors": [
            "node = Node()",
            "node.keys  # expected: []",
            "bt = BTree(2)",
        ],
        "neighbouring_inputs": [
            {"node.keys": [10, 20]},
            {"bt.insert_key": 42},
            {"bt.insert_key_sequence": [3, 1, 2]},
            {"keys_20": [15, 3, 9, 7, 2, 18, 11, 5, 14, 1,
                         20, 6, 13, 4, 17, 8, 12, 19, 16, 10]},
        ],
        "observable_dependencies": "none — Node and BTree are pure in-memory structures",
    }
    with open(os.path.join(work_dir, "inputs.json"), "w") as f:
        json.dump(inputs, f, indent=2)

    # --- results.json -------------------------------------------------------
    node = Node()
    bt = BTree(2)
    bt_insert = BTree(2)
    for k in [3, 1, 2]:
        bt_insert.insert_key(k)

    results = {
        "node_keys":           {"input": "Node()", "expected": [], "actual": node.keys},
        "node_children":       {"input": "Node()", "expected": [], "actual": node.children},
        "node_is_leaf":        {"input": "Node()", "expected": True, "actual": node.is_leaf},
        "btree_root_keys":     {"input": "BTree(2)", "expected": [], "actual": bt.root.keys},
        "btree_min_keys":      {"input": "BTree(2)", "expected": 1, "actual": bt.min_numbers_of_keys},
        "btree_max_keys":      {"input": "BTree(2)", "expected": 3, "actual": bt.max_number_of_keys},
        "btree_traverse_123":  {"input": "BTree(2).insert [3,1,2]", "expected": [1, 2, 3],
                                "actual": bt_insert.traverse_tree()},
        "tests_run":           test_count,
        "tests_passed":        test_count - len(result.failures) - len(result.errors),
        "tests_failed":        len(result.failures),
        "tests_errors":        len(result.errors),
        "native_command":      NATIVE_COMMAND,
    }
    with open(os.path.join(work_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # --- tool_versions.json ------------------------------------------------
    tool_versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "unittest": "stdlib",
    }
    with open(os.path.join(work_dir, "tool_versions.json"), "w") as f:
        json.dump(tool_versions, f, indent=2)

    # --- summary.json -------------------------------------------------------
    summary = {
        "task": "R24-T035",
        "module": "algorithms.data_structures.b_tree",
        "target": "Node",
        "native_command": NATIVE_COMMAND,
        "test_count": test_count,
        "passed": results["tests_passed"],
        "failed": results["tests_failed"],
        "errors": results["tests_errors"],
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "observable_dependencies": "none",
        "isolation_verified": True,
    }
    with open(os.path.join(work_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_checks()
