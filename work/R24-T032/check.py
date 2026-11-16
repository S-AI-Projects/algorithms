#!/usr/bin/env python3
"""
Focused runner and verification script for Task R24-T032.

Checks:
1. Native check: Runs focused Python tests using project test configuration (unittest)
   with external I/O mocked, importing/invoking only the named module (TestPrimeTest).
   Records actual command and nonzero test count.
2. Boundary behavior & Partitioning:
   - Identifies the smallest supported domain around prime_check.
   - Partitions domain into valid interior, valid boundary, and cites source contract.
   - Tests on each side of documented boundaries around 1, 2, 9, and 11.
   - Verifies sieve through 12 respecting exclusive upper-bound interface: [2, 3, 5, 7, 11].
   - Every assertion has an explicit expected value.
3. Preserves existing supported behavior and public interface (no arbitrary TypeError/RangeError policy).
4. Saves all inputs, expected vs actual results, and tool versions to work/R24-T032/.
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

from algorithms.math.prime_check import prime_check


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
    cmd_str = "python3 -m unittest tests.test_math.TestPrimeTest"

    from tests.test_math import TestPrimeTest

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPrimeTest)

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


def run_boundary_checks(out_dir: str) -> tuple[dict, dict]:
    """Execute boundary assertions citing source contract and partitioning domain."""
    boundary_table = [
        {
            "boundary": "around_1_sentinel",
            "source_contract_clause": "algorithms/math/prime_check.py:32 - 'if n <= 1: return False'",
            "description": "Non-positive and unity boundary returning sentinel False",
            "cases": [
                {"input": -1, "side": "below_boundary", "expected": False},
                {"input": 0, "side": "below_boundary", "expected": False},
                {"input": 1, "side": "on_boundary", "expected": False},
            ],
        },
        {
            "boundary": "around_2_smallest_prime",
            "source_contract_clause": "algorithms/math/prime_check.py:34 - 'if n == 2 or n == 3: return True'",
            "description": "Transition from non-prime (<= 1) to smallest prime (2)",
            "cases": [
                {"input": 1, "side": "below_boundary", "expected": False},
                {"input": 2, "side": "on_boundary_smallest_prime", "expected": True},
                {"input": 3, "side": "above_boundary_interior_prime", "expected": True},
            ],
        },
        {
            "boundary": "around_9_first_odd_composite",
            "source_contract_clause": "algorithms/math/prime_check.py:36 - 'if n % 2 == 0 or n % 3 == 0: return False'",
            "description": "Smallest odd composite number (9 = 3*3)",
            "cases": [
                {"input": 8, "side": "below_boundary", "expected": False},
                {"input": 9, "side": "on_boundary_smallest_odd_composite", "expected": False},
                {"input": 10, "side": "above_boundary", "expected": False},
            ],
        },
        {
            "boundary": "around_11_sieve_limit",
            "source_contract_clause": "algorithms/math/prime_check.py:38-43 - 'while j * j <= n: ... return True'",
            "description": "Prime boundary around 11 before exclusive upper bound 12",
            "cases": [
                {"input": 10, "side": "below_boundary", "expected": False},
                {"input": 11, "side": "on_boundary_prime", "expected": True},
                {"input": 12, "side": "above_boundary_composite", "expected": False},
            ],
        },
        {
            "boundary": "sieve_through_12_exclusive_interface",
            "source_contract_clause": "Exclusive upper bound < 12 interface; primes in [0, 12) are 2, 3, 5, 7, 11",
            "description": "Primes less than 12",
            "cases": [
                {
                    "range_exclusive": 12,
                    "expected_primes": [2, 3, 5, 7, 11],
                }
            ],
        },
    ]

    inputs_meta = {
        "module": "algorithms/math/prime_check.py",
        "domain_partitions": {
            "valid_boundary": [-1, 0, 1, 2, 8, 9, 10, 11, 12],
            "valid_interior": [3, 5, 7],
            "undefined_behavior_policy": "No arbitrary TypeError/RangeError imposed; left unconstrained per spec",
        },
        "boundary_table": boundary_table,
    }

    with open(os.path.join(out_dir, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(inputs_meta, f, indent=2)

    results_list = []

    # Assert individual boundaries
    for b_group in boundary_table[:-1]:
        for c in b_group["cases"]:
            val = c["input"]
            expected = c["expected"]
            actual = prime_check(val)
            assert actual == expected, (
                f"Boundary assertion failed for {val}: actual {actual} != expected {expected}"
            )
            results_list.append({
                "boundary": b_group["boundary"],
                "input": val,
                "side": c["side"],
                "expected": expected,
                "actual": actual,
                "pass": True,
            })

    # Assert sieve through 12 with exclusive upper bound
    sieve_upper = 12
    sieve_primes_actual = [n for n in range(sieve_upper) if prime_check(n)]
    expected_sieve_primes = [2, 3, 5, 7, 11]
    assert sieve_primes_actual == expected_sieve_primes, (
        f"Sieve through 12 failed: {sieve_primes_actual} != {expected_sieve_primes}"
    )

    results_data = {
        "individual_boundary_checks": results_list,
        "sieve_through_12_exclusive": {
            "upper_bound_exclusive": sieve_upper,
            "expected_primes": expected_sieve_primes,
            "actual_primes": sieve_primes_actual,
            "pass": True,
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
    print("TASK R24-T032: Focused Runner & Boundary Checks (prime_check)")
    print("=" * 60)

    # 1. Tool versions
    versions = record_tool_versions(out_dir)
    print(f"[1/3] Tool Versions recorded: Python {platform.python_version()} | {versions['git_version']}")

    # 2. Native check
    native_res = run_native_checks(out_dir)
    print(f"[2/3] Native Check: Ran {native_res['command']}")
    print(f"      Tests executed: {native_res['test_count']} (Nonzero test count: OK)")
    print(f"      Status: {'PASSED' if native_res['success'] else 'FAILED'}")

    # 3. Boundary checks
    inputs_meta, results_data = run_boundary_checks(out_dir)
    print("[3/3] Boundary Checks (Citing Source Contract):")
    for r in results_data["individual_boundary_checks"]:
        print(f"      - [{r['boundary']}] input {r['input']:2d} ({r['side']}): expected {r['expected']} -> actual {r['actual']} (OK)")
    print(f"      - Sieve through 12 (<12): {results_data['sieve_through_12_exclusive']['actual_primes']} (OK)")

    summary = {
        "task": "R24-T032",
        "module": "algorithms/math/prime_check.py",
        "public_contract": {
            "inputs": "n: int (integer to test)",
            "result": "bool (True if n is prime, False otherwise)",
            "mutation_behavior": "Pure function; does not mutate inputs or global state",
            "external_dependencies": "None (pure Python built-ins)",
        },
        "native_check": native_res,
        "boundary_results": results_data,
        "status": "ALL_CHECKS_PASSED",
    }

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nAll checks completed successfully. Artifacts saved to work/R24-T032/.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"\nCHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
