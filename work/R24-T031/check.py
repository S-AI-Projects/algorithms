#!/usr/bin/env python3
"""
Focused runner and verification script for Task R24-T031.

Checks:
1. Native check: Runs focused Python tests using project test configuration (unittest)
   with external I/O mocked, importing/invoking only the named module.
   Records actual command and nonzero test count.
2. Distinct behavior regression checks:
   - Ordinary input: [3, 1, 2] -> expected [1, 2, 3]
   - Repeated-value boundary: [2, 2, 1] -> expected [1, 2, 2]
   - Already ordered: [1, 2, 3] -> expected [1, 2, 3]
   - Reversed: [3, 2, 1] -> expected [1, 2, 3]
   - Smallest supported collections: [] -> expected [] and [1] -> expected [1]
3. Separate verification of:
   - Returned value
   - Observable in-place mutation (contract agreement & object identity)
4. Saves all inputs, expected vs actual results, and tool versions to work/R24-T031/.
"""

import copy
import io
import json
import os
import platform
import subprocess
import sys
import unittest
from unittest import mock

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.sorting.cycle_sort import cycle_sort


def record_tool_versions(out_dir: str) -> dict:
    git_ver = "unknown"
    try:
        git_res = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, check=True
        )
        git_ver = git_res.stdout.strip()
    except Exception:
        pass

    versions = {
        "python_version": sys.version,
        "python_version_tuple": list(sys.version_info),
        "platform": platform.platform(),
        "git_version": git_ver,
        "unittest_framework": "Python standard library unittest",
    }

    with open(os.path.join(out_dir, "tool_versions.json"), "w", encoding="utf-8") as f:
        json.dump(versions, f, indent=2)

    return versions


def run_native_checks(out_dir: str) -> dict:
    """Run focused Python tests using project test configuration with external I/O mocked."""
    cmd_str = "python3 -m unittest -k cycle_sort tests/test_sorting.py"

    from tests.test_sorting import TestSuite

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for method_name in loader.getTestCaseNames(TestSuite):
        if "cycle_sort" in method_name:
            suite.addTest(TestSuite(method_name))

    stream_out = io.StringIO()

    with mock.patch("sys.stdout", stream_out), mock.patch("sys.stderr", stream_out):
        runner = unittest.TextTestRunner(stream=stream_out, verbosity=2)
        test_result = runner.run(suite)

    test_count = test_result.testsRun
    assert test_count > 0, f"Expected nonzero test count, got {test_count}"
    assert test_result.wasSuccessful(), f"Native test suite failed: {test_result.failures}"

    native_info = {
        "command": cmd_str,
        "test_count": test_count,
        "failures_count": len(test_result.failures),
        "errors_count": len(test_result.errors),
        "success": test_result.wasSuccessful(),
        "runner_output": stream_out.getvalue(),
    }

    return native_info


def run_regression_checks(out_dir: str) -> tuple[dict, dict]:
    """Execute focused regression checks asserting content and separate mutation."""

    fixtures = [
        {
            "category": "ordinary",
            "description": "Ordinary unsorted collection",
            "input": [3, 1, 2],
            "expected_returned": [1, 2, 3],
            "expected_mutated": [1, 2, 3],
        },
        {
            "category": "repeated_values",
            "description": "Domain boundary with repeated values",
            "input": [2, 2, 1],
            "expected_returned": [1, 2, 2],
            "expected_mutated": [1, 2, 2],
        },
        {
            "category": "already_ordered",
            "description": "Already ordered ascending collection",
            "input": [1, 2, 3],
            "expected_returned": [1, 2, 3],
            "expected_mutated": [1, 2, 3],
        },
        {
            "category": "reversed",
            "description": "Reverse-ordered collection",
            "input": [3, 2, 1],
            "expected_returned": [1, 2, 3],
            "expected_mutated": [1, 2, 3],
        },
        {
            "category": "smallest_supported_empty",
            "description": "Smallest supported collection: empty list",
            "input": [],
            "expected_returned": [],
            "expected_mutated": [],
        },
        {
            "category": "smallest_supported_single",
            "description": "Smallest supported collection: single element",
            "input": [1],
            "expected_returned": [1],
            "expected_mutated": [1],
        },
    ]

    inputs_meta = {
        "fixtures": fixtures,
        "contract": {
            "interface": "ascending",
            "mutation_behavior": "in-place mutation returning the original list reference",
        },
    }

    with open(os.path.join(out_dir, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(inputs_meta, f, indent=2)

    results = []

    for item in fixtures:
        raw_input = item["input"]
        arr = copy.deepcopy(raw_input)
        ret = cycle_sort(arr)

        # 1. Test returned value
        assert ret == item["expected_returned"], (
            f"Returned mismatch for {raw_input}: actual {ret} != expected {item['expected_returned']}"
        )

        # 2. Test observable mutation separately
        assert arr == item["expected_mutated"], (
            f"Mutation mismatch for {raw_input}: actual mutated {arr} != expected {item['expected_mutated']}"
        )

        # 3. Test object identity
        assert ret is arr, f"Return contract violated: returned object is not the mutated input list for {raw_input}"

        results.append({
            "category": item["category"],
            "input": raw_input,
            "expected_returned": item["expected_returned"],
            "actual_returned": ret,
            "expected_mutated": item["expected_mutated"],
            "actual_mutated": arr,
            "in_place_identity": (ret is arr),
            "status": "PASS",
        })

    results_data = {
        "checks_executed": len(results),
        "results": results,
        "all_passed": True,
    }

    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

    return inputs_meta, results_data


def main():
    out_dir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print("TASK R24-T031: Focused Runner & Regression Checks (cycle_sort)")
    print("=" * 60)

    # 1. Tool versions
    versions = record_tool_versions(out_dir)
    print(f"[1/3] Tool Versions recorded: Python {platform.python_version()} | {versions['git_version']}")

    # 2. Native check
    native_res = run_native_checks(out_dir)
    print(f"[2/3] Native Check: Ran {native_res['command']}")
    print(f"      Tests executed: {native_res['test_count']} (Nonzero test count: OK)")
    print(f"      Status: {'PASSED' if native_res['success'] else 'FAILED'}")

    # 3. Distinct behavior regression checks
    inputs_meta, results_data = run_regression_checks(out_dir)
    print("[3/3] Regression Checks (Distinct Behaviors):")
    for r in results_data["results"]:
        print(f"      - [{r['category']}] input: {r['input']}")
        print(f"        Returned: {r['actual_returned']} (expected: {r['expected_returned']})")
        print(f"        Mutated:  {r['actual_mutated']} (expected: {r['expected_mutated']}) | in-place identity: {r['in_place_identity']}")

    summary = {
        "task": "R24-T031",
        "module": "algorithms/sorting/cycle_sort.py",
        "public_contract": {
            "inputs": "array: list[int] (mutable sequence of integers)",
            "result": "list[int] (the sorted list in ascending order)",
            "mutation_behavior": "In-place mutation of input list; returns reference to the same list object",
            "external_dependencies": "None (pure Python built-ins)",
        },
        "native_check": native_res,
        "regression_results": results_data,
        "status": "ALL_CHECKS_PASSED",
    }

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nAll checks completed successfully. Artifacts saved to work/R24-T031/.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"\nCHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
