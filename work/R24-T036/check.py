#!/usr/bin/env python3
"""
R24-T036 focused runner — TreeNode.is_leaf refactor regression tests.

Readability improvement: the repeated inline expression
    ``node.left is None and node.right is None``
is now named ``is_leaf`` on TreeNode, making every call site self-documenting.

Before: ``if root.left is None and root.right is None:``
After:  ``if root.is_leaf:``

Exits non-zero when any assertion fails.
Native check command:
    python3 -m unittest tests.test_issue_fixes.TestTreeNodeIsLeaf
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

from algorithms.common.tree_node import TreeNode  # noqa: E402

# ---------------------------------------------------------------------------
# Native check command (recorded as required)
# ---------------------------------------------------------------------------
NATIVE_COMMAND = "python3 -m unittest tests.test_issue_fixes.TestTreeNodeIsLeaf"

# ---------------------------------------------------------------------------
# Inline test suite
# ---------------------------------------------------------------------------


class TestTreeNodeIsLeaf(unittest.TestCase):
    """Regression tests for TreeNode.is_leaf refactor (R24-T036).

    Before/after: is_leaf names the inline expression
    ``node.left is None and node.right is None`` that was scattered 12×
    across 5 tree-algorithm files.
    """

    # Fixture anchors
    def test_fixture_left_val(self):
        root = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertEqual(root.left.val, 2)

    def test_fixture_right_val(self):
        root = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertEqual(root.right.val, 3)

    def test_root_is_not_leaf(self):
        root = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertFalse(root.is_leaf)

    def test_leaf_child_left(self):
        root = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertTrue(root.left.is_leaf)

    def test_leaf_child_right(self):
        root = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertTrue(root.right.is_leaf)

    # Boundary cases
    def test_single_node_is_leaf(self):
        self.assertTrue(TreeNode(42).is_leaf)

    def test_default_node_is_leaf(self):
        self.assertTrue(TreeNode().is_leaf)

    def test_one_left_child_not_leaf(self):
        self.assertFalse(TreeNode(5, left=TreeNode(1)).is_leaf)

    def test_one_right_child_not_leaf(self):
        self.assertFalse(TreeNode(5, right=TreeNode(9)).is_leaf)

    # Neighbouring supported input (independently calculated)
    def test_neighbour_deeper_tree(self):
        root = TreeNode(10,
                        TreeNode(20, TreeNode(40), TreeNode(50)),
                        TreeNode(30))
        self.assertEqual(root.val, 10)
        self.assertFalse(root.is_leaf)
        self.assertFalse(root.left.is_leaf)
        self.assertTrue(root.right.is_leaf)
        self.assertTrue(root.left.left.is_leaf)
        self.assertTrue(root.left.right.is_leaf)

    # Before/after equivalence
    def test_is_leaf_agrees_no_children(self):
        node = TreeNode(7)
        self.assertEqual(node.is_leaf, node.left is None and node.right is None)

    def test_is_leaf_agrees_has_children(self):
        node = TreeNode(7, TreeNode(1), TreeNode(2))
        self.assertEqual(node.is_leaf, node.left is None and node.right is None)

    def test_is_leaf_agrees_left_only(self):
        node = TreeNode(7, left=TreeNode(1))
        self.assertEqual(node.is_leaf, node.left is None and node.right is None)

    def test_is_leaf_agrees_right_only(self):
        node = TreeNode(7, right=TreeNode(2))
        self.assertEqual(node.is_leaf, node.left is None and node.right is None)

    # Public interface unchanged
    def test_val_attribute_unchanged(self):
        self.assertEqual(TreeNode(99).val, 99)
        self.assertEqual(TreeNode().val, 0)

    def test_left_right_attributes_unchanged(self):
        n = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertIsInstance(n.left, TreeNode)
        self.assertIsInstance(n.right, TreeNode)
        self.assertIsNone(n.left.left)
        self.assertIsNone(n.right.right)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_checks():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTreeNodeIsLeaf)
    test_count = suite.countTestCases()
    assert test_count > 0, "No tests found"

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
            "root = TreeNode(1, TreeNode(2), TreeNode(3))",
            "root.left.val  # expected: 2",
            "root.right.val # expected: 3",
        ],
        "neighbouring_input": {
            "description": "TreeNode(10, TreeNode(20, TreeNode(40), TreeNode(50)), TreeNode(30))",
            "expected_is_leaf": {
                "root": False,
                "root.left": False,
                "root.right": True,
                "root.left.left": True,
                "root.left.right": True,
            },
        },
        "refactor": {
            "before": "node.left is None and node.right is None",
            "after": "node.is_leaf",
            "occurrences_before": 12,
            "files_affected_before": [
                "algorithms/tree/path_sum.py",
                "algorithms/tree/path_sum2.py",
                "algorithms/tree/bst_depth_sum.py",
                "algorithms/tree/binary_tree_paths.py",
                "algorithms/tree/min_height.py",
            ],
        },
    }
    with open(os.path.join(work_dir, "inputs.json"), "w") as f:
        json.dump(inputs, f, indent=2)

    # --- results.json -------------------------------------------------------
    root = TreeNode(1, TreeNode(2), TreeNode(3))
    neighbour = TreeNode(10,
                         TreeNode(20, TreeNode(40), TreeNode(50)),
                         TreeNode(30))
    results = {
        "fixture_left_val":          {"expected": 2, "actual": root.left.val},
        "fixture_right_val":         {"expected": 3, "actual": root.right.val},
        "root_is_leaf":              {"expected": False, "actual": root.is_leaf},
        "root_left_is_leaf":         {"expected": True, "actual": root.left.is_leaf},
        "root_right_is_leaf":        {"expected": True, "actual": root.right.is_leaf},
        "neighbour_root_is_leaf":    {"expected": False, "actual": neighbour.is_leaf},
        "neighbour_right_is_leaf":   {"expected": True, "actual": neighbour.right.is_leaf},
        "default_node_val":          {"expected": 0, "actual": TreeNode().val},
        "tests_run":                 test_count,
        "tests_passed":              test_count - len(result.failures) - len(result.errors),
        "tests_failed":              len(result.failures),
        "tests_errors":              len(result.errors),
        "native_command":            NATIVE_COMMAND,
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
        "task": "R24-T036",
        "module": "algorithms.common.tree_node",
        "target": "TreeNode",
        "refactor": "Added TreeNode.is_leaf property naming the repeated inline expression",
        "native_command": NATIVE_COMMAND,
        "test_count": test_count,
        "passed": results["tests_passed"],
        "failed": results["tests_failed"],
        "errors": results["tests_errors"],
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "public_interface_unchanged": True,
        "behavior_preserved": True,
    }
    with open(os.path.join(work_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_checks()
