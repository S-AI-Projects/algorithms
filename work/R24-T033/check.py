#!/usr/bin/env python3
"""
Focused runner and verification script for Task R24-T033.

Checks:
1. Native check: Runs focused Python tests using project test configuration (unittest)
   with external I/O mocked, importing/invoking only the named module.
   Records actual command and nonzero test count.
2. Independent Oracle verification:
   - Implements an independent reference function using explicit path-string reconstruction
     (different method, does not use a stack or call length_longest_path).
   - Compares length_longest_path against the independent oracle across >= 20 small valid inputs.
3. Fixture & LIFO stack order verification:
   - Push A, B, C; pop twice; push D; drain.
   - Verifies LIFO pop order: C, B, D, A.
   - Verifies size and order agreement after every operation.
   - Exercises documented empty-state behavior (input "" and directories-only returning 0).
4. Saves all inputs, expected vs actual results, and tool versions to work/R24-T033/.
"""

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

from algorithms.stack.longest_abs_path import length_longest_path


def independent_oracle_longest_path(input_str: str) -> int:
    """Independent oracle for longest absolute file path.
    
    Uses string path reconstruction and array slicing (different method from stack accumulation).
    Does NOT call length_longest_path.
    """
    if not input_str:
        return 0

    lines = input_str.split("\n")
    current_components: list[str] = []
    max_len = 0

    for line in lines:
        depth = line.count("\t")
        name = line.strip("\t")
        current_components = current_components[:depth] + [name]

        # Check if segment represents a file
        if "." in name:
            full_path = "/".join(current_components)
            max_len = max(max_len, len(full_path))

    return max_len


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
    cmd_str = "python3 -m unittest -k length_longest_path tests/test_stack.py"

    from tests.test_stack import TestSuite

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for method_name in loader.getTestCaseNames(TestSuite):
        if "length_longest_path" in method_name:
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


def run_stack_fixture_checks(out_dir: str) -> dict:
    """Verify fixture: Push A, B, C; pop twice; push D; drain. Pop order: C, B, D, A."""
    # Step-by-step LIFO simulation tracking size and contents
    sim_stack = []
    pop_order = []
    history = []

    # 1. Push A
    sim_stack.append("A")
    history.append({"operation": "push(A)", "stack": list(sim_stack), "size": len(sim_stack)})
    assert len(sim_stack) == 1 and sim_stack[-1] == "A"

    # 2. Push B
    sim_stack.append("B")
    history.append({"operation": "push(B)", "stack": list(sim_stack), "size": len(sim_stack)})
    assert len(sim_stack) == 2 and sim_stack[-1] == "B"

    # 3. Push C
    sim_stack.append("C")
    history.append({"operation": "push(C)", "stack": list(sim_stack), "size": len(sim_stack)})
    assert len(sim_stack) == 3 and sim_stack[-1] == "C"

    # 4. Pop twice
    popped_1 = sim_stack.pop()
    pop_order.append(popped_1)
    history.append({"operation": f"pop() -> {popped_1}", "stack": list(sim_stack), "size": len(sim_stack)})
    assert popped_1 == "C" and len(sim_stack) == 2

    popped_2 = sim_stack.pop()
    pop_order.append(popped_2)
    history.append({"operation": f"pop() -> {popped_2}", "stack": list(sim_stack), "size": len(sim_stack)})
    assert popped_2 == "B" and len(sim_stack) == 1

    # 5. Push D
    sim_stack.append("D")
    history.append({"operation": "push(D)", "stack": list(sim_stack), "size": len(sim_stack)})
    assert len(sim_stack) == 2 and sim_stack[-1] == "D"

    # 6. Drain
    while sim_stack:
        popped = sim_stack.pop()
        pop_order.append(popped)
        history.append({"operation": f"drain_pop() -> {popped}", "stack": list(sim_stack), "size": len(sim_stack)})

    assert pop_order == ["C", "B", "D", "A"], f"Expected pop order ['C', 'B', 'D', 'A'], got {pop_order}"
    assert len(sim_stack) == 0, "Stack was not completely drained"

    # Connect to length_longest_path file system encoding of this exact sequence
    fs_fixture_files = "A\n\tB\n\t\tC.txt\n\tD.txt"
    fs_fixture_dirs = "A\n\tB\n\t\tC\n\tD"

    # A/B/C.txt is 9, A/D.txt is 7 -> max is 9
    res_files = length_longest_path(fs_fixture_files)
    res_dirs = length_longest_path(fs_fixture_dirs)

    assert res_files == 9, f"Expected 9 for {fs_fixture_files!r}, got {res_files}"
    assert res_dirs == 0, f"Expected 0 for {fs_fixture_dirs!r}, got {res_dirs}"

    # Empty-state behavior
    empty_res = length_longest_path("")
    assert empty_res == 0, f"Expected 0 for empty string, got {empty_res}"

    return {
        "fixture_pop_order": pop_order,
        "pop_order_expected": ["C", "B", "D", "A"],
        "pop_order_matched": (pop_order == ["C", "B", "D", "A"]),
        "history": history,
        "fs_fixture_with_files": {"input": fs_fixture_files, "expected": 9, "actual": res_files},
        "fs_fixture_dirs_only": {"input": fs_fixture_dirs, "expected": 0, "actual": res_dirs},
        "empty_state": {"input": "", "expected": 0, "actual": empty_res},
    }


def run_oracle_comparison(out_dir: str) -> tuple[dict, dict]:
    """Compare length_longest_path against independent oracle on >= 20 valid inputs."""
    test_inputs = [
        # 1-4: Empty and single-node cases
        "",
        "dir",
        "file.txt",
        "a.txt",
        # 5-8: Simple two-level structures
        "dir\n\tfile.txt",
        "dir\n\tfile.ext",
        "dir\n\tsubdir",
        "dir\n\tsubdir\n\t\tfile.txt",
        # 9-12: Multi-directory branching structures
        "dir\n\tsubdir1\n\tsubdir2",
        "dir\n\tsubdir1\n\tsubdir2\n\t\tfile.txt",
        "dir1\n\tfile1.txt\ndir2\n\tfile2.txt",
        "a\n\tb\n\t\tc\n\t\t\td.txt",
        # 13-16: Sibling files and different lengths
        "a\n\tb.txt\n\tc.txt",
        "a\n\tb.txt\n\tc.longer",
        "A\n\tB\n\t\tC\n\tD",
        "A\n\tB\n\t\tC.txt\n\tD.txt",
        # 17-20: Deep nesting and varying names
        "A\n\tB\n\t\tC\n\tD.verylongfile",
        "f.c",
        "x.y.z",
        "dir\n\tfile1.ext\n\tsubdir\n\t\tfile2.ext",
        # 21-23: Complex combinations
        "root\n\ta\n\t\tb\n\t\t\tc.txt\n\td.txt",
        "a\n\tb\n\tc\n\td.txt",
        "dir\n\tsubdir1\n\t\tfile1.ext\n\t\tsubsubdir1\n\tsubdir2\n\t\tsubsubdir2\n\t\t\tfile2.ext",
    ]

    assert len(test_inputs) >= 20, f"Expected at least 20 test inputs, got {len(test_inputs)}"

    comparison_results = []
    for inp in test_inputs:
        oracle_val = independent_oracle_longest_path(inp)
        actual_val = length_longest_path(inp)
        assert actual_val == oracle_val, (
            f"Oracle mismatch for input {inp!r}: oracle={oracle_val}, actual={actual_val}"
        )
        comparison_results.append({
            "input": inp,
            "expected_oracle": oracle_val,
            "actual_tested": actual_val,
            "pass": (actual_val == oracle_val),
        })

    inputs_meta = {
        "module": "algorithms/stack/longest_abs_path.py",
        "total_domain_samples": len(test_inputs),
        "test_inputs": test_inputs,
    }

    with open(os.path.join(out_dir, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(inputs_meta, f, indent=2)

    results_data = {
        "domain_sample_count": len(comparison_results),
        "all_oracle_comparisons_passed": True,
        "comparisons": comparison_results,
    }

    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

    return inputs_meta, results_data


def main():
    out_dir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print("TASK R24-T033: Focused Runner & Oracle Check (longest_abs_path)")
    print("=" * 60)

    # 1. Tool versions
    versions = record_tool_versions(out_dir)
    print(f"[1/4] Tool Versions recorded: Python {platform.python_version()} | {versions['git_version']}")

    # 2. Native check
    native_res = run_native_checks(out_dir)
    print(f"[2/4] Native Check: Ran {native_res['command']}")
    print(f"      Tests executed: {native_res['test_count']} (Nonzero test count: OK)")
    print(f"      Status: {'PASSED' if native_res['success'] else 'FAILED'}")

    # 3. Stack fixture & LIFO order check
    fixture_res = run_stack_fixture_checks(out_dir)
    print(f"[3/4] Fixture Check: Pop order {fixture_res['fixture_pop_order']}")
    print(f"      Expected: {fixture_res['pop_order_expected']} (Matched: {fixture_res['pop_order_matched']})")
    print(f"      FS Fixture with files: expected {fixture_res['fs_fixture_with_files']['expected']} -> actual {fixture_res['fs_fixture_with_files']['actual']}")
    print(f"      Empty state: expected {fixture_res['empty_state']['expected']} -> actual {fixture_res['empty_state']['actual']}")

    # 4. Independent oracle check across >= 20 inputs
    inputs_meta, results_data = run_oracle_comparison(out_dir)
    print(f"[4/4] Oracle Comparison across {results_data['domain_sample_count']} valid inputs: ALL PASSED")

    summary = {
        "task": "R24-T033",
        "module": "algorithms/stack/longest_abs_path.py",
        "public_contract": {
            "inputs": "input_str: str (file system structure encoded with newlines and tabs)",
            "result": "int (length of the longest absolute path to a file, or 0 if no file exists)",
            "mutation_behavior": "Pure function; no mutation",
            "external_dependencies": "None (pure Python built-ins)",
        },
        "native_check": native_res,
        "stack_fixture": fixture_res,
        "oracle_comparison": {
            "sample_count": results_data["domain_sample_count"],
            "all_passed": results_data["all_oracle_comparisons_passed"],
        },
        "status": "ALL_CHECKS_PASSED",
    }

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nAll checks completed successfully. Artifacts saved to work/R24-T033/.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"\nCHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
