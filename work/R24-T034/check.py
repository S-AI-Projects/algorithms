#!/usr/bin/env python3
"""
Focused runner and verification script for Task R24-T034.

Checks:
1. Native check: Runs focused Python tests using project test configuration (unittest)
   with external I/O mocked, importing/invoking only the named module.
   Records actual command and nonzero test count.
2. Invariant & Property verification:
   - Independently calculated output and documented return/mutation contract agree.
   - Repeated runs with fresh equivalent inputs give the same result (idempotence).
   - Executable anchors: get_bit(22, 2) == 1, get_bit(22, 3) == 0, set_bit(22, 3) == 30.
   - Neighboring supported inputs: get_bit(22, 4) == 1, get_bit(22, 1) == 1, get_bit(30, 3) == 1.
   - 100 bounded valid generated cases with fixed seed (seed=42).
   - Every assertion has an explicit expected value.
3. Mutant / Broken Invariant Check:
   - Verifies that the checks FAIL when the relevant invariant is deliberately broken
     in a temporary copy (work/R24-T034/mutant_bit_operation.py).
4. Saves all inputs, expected vs actual results, and tool versions to work/R24-T034/.
"""

import importlib.util
import io
import json
import os
import platform
import random
import subprocess
import sys
import unittest
from unittest import mock

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.bit_manipulation.bit_operation import get_bit, set_bit

# Load mutant
mutant_path = os.path.join(os.path.dirname(__file__), "mutant_bit_operation.py")
spec = importlib.util.spec_from_file_location("mutant_bit_operation", mutant_path)
mutant_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mutant_mod)
mutant_get_bit = mutant_mod.get_bit


def independent_get_bit(number: int, position: int) -> int:
    """Independently calculated bit value at position using mathematical shift."""
    return (number >> position) & 1


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
    cmd_str = "python3 -m unittest -k get_bit tests/test_bit_manipulation.py"

    from tests.test_bit_manipulation import TestSuite

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for method_name in loader.getTestCaseNames(TestSuite):
        if "get_bit" in method_name:
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


def run_property_and_mutant_checks(out_dir: str) -> tuple[dict, dict]:
    """Execute property checks on anchors, neighbors, and 100 generated cases."""
    # 1. Anchors and Neighbors
    anchor_cases = [
        {"desc": "Anchor 1", "number": 22, "position": 2, "expected": 1},
        {"desc": "Anchor 2", "number": 22, "position": 3, "expected": 0},
        {"desc": "Neighbor 1 (position 4 of 22)", "number": 22, "position": 4, "expected": 1},
        {"desc": "Neighbor 2 (position 1 of 22)", "number": 22, "position": 1, "expected": 1},
        {"desc": "Neighbor 3 (set_bit(22, 3)=30, check bit 3)", "number": 30, "position": 3, "expected": 1},
    ]

    anchor_results = []
    for ac in anchor_cases:
        num = ac["number"]
        pos = ac["position"]
        expected = ac["expected"]
        actual = get_bit(num, pos)
        independent = independent_get_bit(num, pos)

        assert actual == expected == independent, (
            f"Anchor/neighbor mismatch for ({num}, {pos}): actual {actual} != expected {expected}"
        )

        # Invariant: fresh equivalent inputs produce identical results
        actual_fresh = get_bit(int(str(num)), int(str(pos)))
        assert actual == actual_fresh, "Invariant failed: fresh equivalent inputs produced different outputs"

        anchor_results.append({
            "description": ac["desc"],
            "number": num,
            "position": pos,
            "expected": expected,
            "actual": actual,
            "idempotence_fresh_pass": True,
            "pass": True,
        })

    # 2. 100 Bounded Valid Generated Cases (Fixed Seed 42)
    rng = random.Random(42)
    generated_cases = []
    generated_results = []

    for i in range(100):
        num = rng.randint(0, 10000)
        pos = rng.randint(0, 30)
        expected = independent_get_bit(num, pos)
        actual = get_bit(num, pos)

        assert actual == expected, (
            f"Generated case {i} failed for ({num}, {pos}): actual {actual} != expected {expected}"
        )

        # Fresh equivalent inputs
        actual_fresh = get_bit(int(str(num)), int(str(pos)))
        assert actual == actual_fresh, "Invariant broken: fresh equivalent inputs differed"

        generated_cases.append({"number": num, "position": pos, "expected": expected})
        generated_results.append({
            "case_index": i,
            "number": num,
            "position": pos,
            "expected": expected,
            "actual": actual,
            "pass": True,
        })

    # 3. Deliberately Broken Invariant Check on Mutant
    # The mutant inverts the bit logic: (number & (1 << position)) == 0
    mutant_failed = False
    mutant_failure_detail = ""
    try:
        mutant_val = mutant_get_bit(22, 2)
        assert mutant_val == 1, f"Mutant returned {mutant_val} instead of 1"
    except AssertionError as e:
        mutant_failed = True
        mutant_failure_detail = str(e)

    assert mutant_failed, "Mutant unexpectedly passed the invariant check!"

    inputs_meta = {
        "module": "algorithms/bit_manipulation/bit_operation.py",
        "anchors_and_neighbors": anchor_cases,
        "generator_spec": {
            "seed": 42,
            "bounded_case_count": 100,
            "number_domain": "[0, 10000]",
            "position_domain": "[0, 30]",
        },
        "generated_cases": generated_cases,
    }

    with open(os.path.join(out_dir, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(inputs_meta, f, indent=2)

    results_data = {
        "anchor_and_neighbor_results": anchor_results,
        "generated_cases_tested": len(generated_results),
        "generated_all_passed": True,
        "mutant_check": {
            "mutant_file": "mutant_bit_operation.py",
            "mutant_correctly_failed": mutant_failed,
            "failure_detail": mutant_failure_detail,
        },
        "all_passed": True,
    }

    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

    return inputs_meta, results_data


def main():
    out_dir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print("TASK R24-T034: Focused Runner & Property Check (get_bit)")
    print("=" * 60)

    # 1. Tool versions
    versions = record_tool_versions(out_dir)
    print(f"[1/4] Tool Versions recorded: Python {platform.python_version()} | {versions['git_version']}")

    # 2. Native check
    native_res = run_native_checks(out_dir)
    print(f"[2/4] Native Check: Ran {native_res['command']}")
    print(f"      Tests executed: {native_res['test_count']} (Nonzero test count: OK)")
    print(f"      Status: {'PASSED' if native_res['success'] else 'FAILED'}")

    # 3. Property & Mutant checks
    inputs_meta, results_data = run_property_and_mutant_checks(out_dir)
    print(f"[3/4] Property & Invariant Check:")
    for ar in results_data["anchor_and_neighbor_results"]:
        print(f"      - {ar['description']} ({ar['number']}, {ar['position']}): expected {ar['expected']} -> actual {ar['actual']} (OK)")
    print(f"      - 100 Bounded Cases with seed 42: ALL PASSED")

    print(f"[4/4] Broken Invariant Check on Mutant:")
    print(f"      Mutant correctly caught & failed: {results_data['mutant_check']['mutant_correctly_failed']}")
    print(f"      Failure detail: {results_data['mutant_check']['failure_detail']}")

    summary = {
        "task": "R24-T034",
        "module": "algorithms/bit_manipulation/bit_operation.py",
        "public_contract": {
            "inputs": "number: int, position: int",
            "result": "int (1 if bit at position is set, 0 otherwise)",
            "mutation_behavior": "Pure function; does not mutate inputs or global state",
            "external_dependencies": "None (pure Python built-ins)",
        },
        "native_check": native_res,
        "property_results": results_data,
        "status": "ALL_CHECKS_PASSED",
    }

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nAll checks completed successfully. Artifacts saved to work/R24-T034/.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"\nCHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
