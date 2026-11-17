#!/usr/bin/env python3
"""
R24-T037 focused runner — bogo_sort worked example and state transition checks.

Exits non-zero when any assertion fails.
Native check command:
    python3 -m unittest tests.test_sorting.TestBogoSortWorkedExample
"""

import json
import os
import platform
import sys
import unittest
from io import StringIO
from unittest import mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.sorting.bogo_sort import bogo_sort  # noqa: E402

NATIVE_COMMAND = "python3 -m unittest tests.test_sorting.TestBogoSortWorkedExample"


class TestBogoSortWorkedExample(unittest.TestCase):
    def test_fixture_3_1_2(self):
        import random; random.seed(0)
        self.assertEqual(bogo_sort([3, 1, 2]), [1, 2, 3])

    def test_fixture_2_2_1(self):
        import random; random.seed(0)
        self.assertEqual(bogo_sort([2, 2, 1]), [1, 2, 2])

    def test_fixture_already_sorted(self):
        import random; random.seed(0)
        self.assertEqual(bogo_sort([1, 2, 3]), [1, 2, 3])

    def test_fixture_reversed(self):
        import random; random.seed(42)
        self.assertEqual(bogo_sort([3, 2, 1]), [1, 2, 3])

    def test_fixture_smallest_collection(self):
        self.assertEqual(bogo_sort([1]), [1])

    def test_returns_same_object(self):
        import random; random.seed(0)
        arr = [3, 1, 2]
        result = bogo_sort(arr)
        self.assertIs(result, arr)
        self.assertEqual(arr, [1, 2, 3])

    def test_already_sorted_no_shuffle_needed(self):
        from unittest.mock import patch
        arr = [1, 2, 3]
        with patch("random.shuffle") as mock_shuffle:
            result = bogo_sort(arr)
        mock_shuffle.assert_not_called()
        self.assertEqual(result, [1, 2, 3])

    def test_single_element_no_shuffle_needed(self):
        from unittest.mock import patch
        with patch("random.shuffle") as mock_shuffle:
            result = bogo_sort([7])
        mock_shuffle.assert_not_called()
        self.assertEqual(result, [7])

    def test_docstring_example_3_1_2(self):
        import random; random.seed(0)
        self.assertEqual(bogo_sort([3, 1, 2]), [1, 2, 3])

    def test_docstring_example_already_sorted(self):
        import random; random.seed(0)
        self.assertEqual(bogo_sort([1, 2, 3]), [1, 2, 3])

    def test_docstring_example_2_2_1(self):
        import random; random.seed(0)
        self.assertEqual(bogo_sort([2, 2, 1]), [1, 2, 2])

    def test_docstring_example_reversed_seed42(self):
        import random; random.seed(42)
        self.assertEqual(bogo_sort([3, 2, 1]), [1, 2, 3])

    def test_docstring_example_single(self):
        self.assertEqual(bogo_sort([1]), [1])


def run_checks():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBogoSortWorkedExample)
    test_count = suite.countTestCases()
    assert test_count > 0, "No tests found"

    buf = StringIO()
    with mock.patch("sys.stdout", buf), mock.patch("sys.stderr", buf):
        runner = unittest.TextTestRunner(stream=buf, verbosity=2)
        result = runner.run(suite)

    output = buf.getvalue()
    print(output)

    work_dir = os.path.dirname(os.path.abspath(__file__))

    inputs = {
        "fixtures": [
            {"input": [3, 1, 2], "seed": 0, "expected": [1, 2, 3]},
            {"input": [2, 2, 1], "seed": 0, "expected": [1, 2, 2]},
            {"input": [1, 2, 3], "seed": 0, "expected": [1, 2, 3]},
            {"input": [3, 2, 1], "seed": 42, "expected": [1, 2, 3]},
            {"input": [1], "expected": [1]},
        ],
        "decisive_state_transition": (
            "_is_sorted returns True; while-loop terminates immediately. "
            "Shuffle is bypassed entirely for already sorted inputs."
        ),
    }
    with open(os.path.join(work_dir, "inputs.json"), "w") as f:
        json.dump(inputs, f, indent=2)

    import random
    random.seed(0)
    res_312 = bogo_sort([3, 1, 2])
    random.seed(0)
    res_221 = bogo_sort([2, 2, 1])

    results = {
        "fixture_3_1_2": {"expected": [1, 2, 3], "actual": res_312},
        "fixture_2_2_1": {"expected": [1, 2, 2], "actual": res_221},
        "tests_run": test_count,
        "tests_passed": test_count - len(result.failures) - len(result.errors),
        "tests_failed": len(result.failures),
        "tests_errors": len(result.errors),
        "native_command": NATIVE_COMMAND,
    }
    with open(os.path.join(work_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    tool_versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "unittest": "stdlib",
    }
    with open(os.path.join(work_dir, "tool_versions.json"), "w") as f:
        json.dump(tool_versions, f, indent=2)

    summary = {
        "task": "R24-T037",
        "module": "algorithms.sorting.bogo_sort",
        "target": "bogo_sort",
        "native_command": NATIVE_COMMAND,
        "test_count": test_count,
        "passed": results["tests_passed"],
        "failed": results["tests_failed"],
        "errors": results["tests_errors"],
        "status": "PASS" if result.wasSuccessful() else "FAIL",
    }
    with open(os.path.join(work_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_checks()
