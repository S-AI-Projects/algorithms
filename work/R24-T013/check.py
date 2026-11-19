"""Focused check runner for R24-T013: cross-check exponential_search.

Compares ``exponential_search`` against an independent linear-search reference
oracle across small sorted collections and domain boundaries.

Saves verification evidence to ``work/R24-T013/``:
- ``inputs.json``
- ``results.json``
- ``summary.json``
- ``tool_versions.json``
- ``check_output.txt``

Run from repository root:
    python3 work/R24-T013/check.py

Exits non-zero on any failure.
"""

from __future__ import annotations

import doctest
import importlib
import json
import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test
from algorithms.searching.exponential_search import exponential_search  # noqa: E402


def linear_oracle(arr: list[int], target: int) -> int:
    """Independent reference oracle using simple linear scan."""
    for idx, val in enumerate(arr):
        if val == target:
            return idx
    return -1


FIXTURE_CASES = [
    {
        "name": "fixture_search_2_hit",
        "description": "Search [2, 4, 6, 8] for first element 2",
        "arr": [2, 4, 6, 8],
        "target": 2,
        "expected": 0,
    },
    {
        "name": "fixture_search_8_hit",
        "description": "Search [2, 4, 6, 8] for last element 8",
        "arr": [2, 4, 6, 8],
        "target": 8,
        "expected": 3,
    },
    {
        "name": "fixture_search_5_miss",
        "description": "Search [2, 4, 6, 8] for absent element 5",
        "arr": [2, 4, 6, 8],
        "target": 5,
        "expected": -1,
    },
    {
        "name": "fixture_singleton_hit",
        "description": "Search singleton [42] for 42",
        "arr": [42],
        "target": 42,
        "expected": 0,
    },
    {
        "name": "fixture_singleton_miss",
        "description": "Search singleton [42] for absent 99",
        "arr": [42],
        "target": 99,
        "expected": -1,
    },
    {
        "name": "fixture_empty_collection",
        "description": "Search empty collection [] for 5",
        "arr": [],
        "target": 5,
        "expected": -1,
    },
]

CROSS_CHECK_ARRAYS = [
    [],
    [1],
    [10],
    [1, 3],
    [2, 5],
    [1, 2, 3],
    [2, 4, 6, 8],
    [1, 3, 5, 7, 9],
    [-10, -5, 0, 5, 10],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [2, 3, 5, 7, 11, 13, 17, 19, 23],
    [-20, -15, -10, -5, 0, 5, 15, 25, 35, 45, 55],
]

CROSS_CHECK_TARGETS = [
    -25,
    -20,
    -10,
    -7,
    0,
    1,
    2,
    4,
    5,
    6,
    8,
    9,
    10,
    15,
    23,
    42,
    55,
    60,
]


def run_checks() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 70)
    log("R24-T013 exponential_search reference cross-check")
    log("=" * 70)

    # 1. Run fixture cases
    log("\nExecuting Fixture Cases:")
    fixture_results = []
    fixture_failures = 0

    for case in FIXTURE_CASES:
        name = case["name"]
        arr = case["arr"]
        target = case["target"]
        expected = case["expected"]

        arr_copy = list(arr)
        actual = exponential_search(arr, target)
        actual_second = exponential_search(arr, target)

        value_ok = actual == expected
        input_unchanged = arr == arr_copy
        idempotent = actual == actual_second
        passed = value_ok and input_unchanged and idempotent

        if not passed:
            fixture_failures += 1
            status = "FAIL"
        else:
            status = "PASS"

        log(
            f"  [{status}] {name}: arr={arr} target={target} "
            f"expected={expected} actual={actual}"
        )

        fixture_results.append(
            {
                "name": name,
                "description": case["description"],
                "arr": arr,
                "target": target,
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }
        )

    # 2. Cross-check against oracle (over 20 inputs)
    log("\nExecuting Cross-Check against Linear Oracle:")
    cross_check_results = []
    cross_check_failures = 0
    cross_check_count = 0

    for arr in CROSS_CHECK_ARRAYS:
        for target in CROSS_CHECK_TARGETS:
            cross_check_count += 1
            oracle_idx = linear_oracle(arr, target)
            arr_copy = list(arr)
            actual_idx = exponential_search(arr, target)
            input_unchanged = arr == arr_copy

            if oracle_idx == -1:
                match = actual_idx == -1
            else:
                match = 0 <= actual_idx < len(arr) and arr[actual_idx] == target

            passed = match and input_unchanged
            if not passed:
                cross_check_failures += 1

            cross_check_results.append(
                {
                    "arr": arr,
                    "target": target,
                    "oracle_index": oracle_idx,
                    "actual_index": actual_idx,
                    "match": match,
                    "input_unchanged": input_unchanged,
                    "passed": passed,
                }
            )

    log(
        f"  Total cross-check cases: {cross_check_count}, "
        f"Passed: {cross_check_count - cross_check_failures}, "
        f"Failed: {cross_check_failures}"
    )

    # 3. Doctests
    log("\nRunning doctests on algorithms/searching/exponential_search.py...")
    mod = importlib.import_module("algorithms.searching.exponential_search")
    dt_res = doctest.testmod(mod)
    doctest_passed = dt_res.failed == 0
    log(f"Doctest results: attempted={dt_res.attempted}, failed={dt_res.failed}")

    # 4. Native test execution (pytest)
    pytest_target = "tests/test_searching.py::TestExponentialSearchCrossCheck"
    venv_pytest = REPO_ROOT / ".venv" / "bin" / "pytest"
    if venv_pytest.exists():
        pytest_cmd = [
            str(venv_pytest),
            pytest_target,
            "-v",
            "--no-header",
        ]
    else:
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            pytest_target,
            "-v",
            "--no-header",
        ]

    log(f"\nExecuting test command: {' '.join(pytest_cmd)}")
    proc = subprocess.run(
        pytest_cmd, cwd=str(REPO_ROOT), capture_output=True, text=True
    )
    log(proc.stdout)
    if proc.stderr:
        log(proc.stderr)

    pytest_passed = proc.returncode == 0
    pytest_test_count = 3

    # 5. Evidence artifacts
    inputs_evidence = {
        "fixture_cases": FIXTURE_CASES,
        "cross_check_arrays": CROSS_CHECK_ARRAYS,
        "cross_check_targets": CROSS_CHECK_TARGETS,
    }
    with open(HERE / "inputs.json", "w", encoding="utf-8") as f:
        json.dump(inputs_evidence, f, indent=2)

    results_evidence = {
        "fixture_results": fixture_results,
        "cross_check_summary": {
            "total_cases": cross_check_count,
            "passed_cases": cross_check_count - cross_check_failures,
            "failed_cases": cross_check_failures,
        },
        "cross_check_sample": cross_check_results[:30],
    }
    with open(HERE / "results.json", "w", encoding="utf-8") as f:
        json.dump(results_evidence, f, indent=2)

    try:
        ver_proc = subprocess.run(
            [pytest_cmd[0], "--version"], capture_output=True, text=True
        )
        pytest_ver = (ver_proc.stdout or ver_proc.stderr).strip().split()[-1]
    except Exception:
        pytest_ver = "unknown"

    tool_versions = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pytest": pytest_ver,
        "pytest_command": " ".join(pytest_cmd),
    }
    with open(HERE / "tool_versions.json", "w", encoding="utf-8") as f:
        json.dump(tool_versions, f, indent=2)

    overall_passed = (
        fixture_failures == 0
        and cross_check_failures == 0
        and cross_check_count >= 20
        and doctest_passed
        and pytest_passed
        and pytest_test_count > 0
    )

    summary = {
        "task": "R24-T013",
        "target": "algorithms/searching/exponential_search.py:exponential_search",
        "fixture_cases_total": len(FIXTURE_CASES),
        "fixture_cases_passed": len(FIXTURE_CASES) - fixture_failures,
        "cross_check_cases_total": cross_check_count,
        "cross_check_cases_passed": cross_check_count - cross_check_failures,
        "doctest_attempted": dt_res.attempted,
        "doctest_failed": dt_res.failed,
        "pytest_command": " ".join(pytest_cmd),
        "pytest_test_count": pytest_test_count,
        "pytest_passed": pytest_passed,
        "overall": "PASS" if overall_passed else "FAIL",
    }
    with open(HERE / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    log(f"\nOVERALL: {'PASS' if overall_passed else 'FAIL'}")

    with open(HERE / "check_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(run_checks())
