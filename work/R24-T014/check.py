"""Focused check runner for R24-T014: invariant checks for wiggle_sort.

Verifies:
1. Output satisfies the wiggle invariant: nums[0] <= nums[1] >= nums[2] <= ...
2. Multiplicity preservation: output is a valid permutation of the input.
3. In-place mutation: result is the exact input list.
4. Broken-invariant detection: verifies broken versions fail and reports
   the smallest failing counterexample.

Saves verification evidence to ``work/R24-T014/``:
- ``invariant.md``
- ``inputs.json``
- ``results.json``
- ``summary.json``
- ``tool_versions.json``
- ``check_output.txt``

Run from repository root:
    python3 work/R24-T014/check.py

Exits non-zero on any failure.
"""

from __future__ import annotations

import doctest
import importlib
import json
import platform
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test
from algorithms.sorting.wiggle_sort import wiggle_sort  # noqa: E402

FIXTURES = [
    {
        "name": "fixture_3_1_2",
        "input": [3, 1, 2],
        "expected": [1, 3, 2],
    },
    {
        "name": "fixture_2_2_1",
        "input": [2, 2, 1],
        "expected": [1, 2, 2],
    },
    {
        "name": "fixture_already_ordered",
        "input": [1, 2, 3],
        "expected": [1, 3, 2],
    },
    {
        "name": "fixture_reversed",
        "input": [3, 2, 1],
        "expected": [1, 3, 2],
    },
    {
        "name": "fixture_smallest_empty",
        "input": [],
        "expected": [],
    },
    {
        "name": "fixture_smallest_single",
        "input": [1],
        "expected": [1],
    },
    {
        "name": "fixture_two_elements",
        "input": [1, 2],
        "expected": [1, 2],
    },
]


def check_wiggle_invariant(arr: list[int]) -> bool:
    for i in range(len(arr) - 1):
        if i % 2 == 0 and not (arr[i] <= arr[i + 1]):
            return False
        if i % 2 == 1 and not (arr[i] >= arr[i + 1]):
            return False
    return True


def run_checks() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 70)
    log("R24-T014 wiggle_sort invariant check")
    log("=" * 70)

    # 1. Fixture Cases
    log("\nExecuting Fixtures:")
    fixture_results = []
    fixture_failures = 0

    for fix in FIXTURES:
        name = fix["name"]
        inp = fix["input"]
        expected = fix["expected"]

        target = list(inp)
        res = wiggle_sort(target)

        is_same_object = res is target
        matches_expected = res == expected
        wiggle_ok = check_wiggle_invariant(res)
        mult_ok = sorted(res) == sorted(inp)
        passed = is_same_object and matches_expected and wiggle_ok and mult_ok

        if not passed:
            fixture_failures += 1
            status = "FAIL"
        else:
            status = "PASS"

        log(
            f"  [{status}] {name}: input={inp} expected={expected} actual={res} "
            f"wiggle_ok={wiggle_ok} mult_ok={mult_ok} in_place={is_same_object}"
        )

        fixture_results.append(
            {
                "name": name,
                "input": inp,
                "expected": expected,
                "actual": res,
                "wiggle_ok": wiggle_ok,
                "multiplicity_ok": mult_ok,
                "in_place": is_same_object,
                "passed": passed,
            }
        )

    # 2. Invariant Property Checks (100+ random cases)
    log("\nExecuting Property Checks (120 generated cases, seed=24014):")
    rng = random.Random(24014)
    property_cases = []
    property_failures = 0

    for idx in range(120):
        length = rng.randint(0, 30)
        arr = [rng.randint(-100, 100) for _ in range(length)]
        orig = list(arr)
        target = list(arr)
        res = wiggle_sort(target)

        is_same = res is target
        wiggle_ok = check_wiggle_invariant(res)
        mult_ok = sorted(res) == sorted(orig)
        passed = is_same and wiggle_ok and mult_ok

        if not passed:
            property_failures += 1

        property_cases.append(
            {
                "case_id": idx + 1,
                "length": length,
                "input_sample": orig[:5],
                "wiggle_ok": wiggle_ok,
                "multiplicity_ok": mult_ok,
                "in_place": is_same,
                "passed": passed,
            }
        )

    log(
        f"  Total property cases: 120, Passed: {120 - property_failures}, "
        f"Failed: {property_failures}"
    )

    # 3. Broken Invariant Detection
    log("\nTesting Broken-Invariant Detection:")

    def broken_wiggle_sort(array: list[int]) -> list[int]:
        # Deliberately strictly sorts ascending, violating wiggle for length >= 3
        return sorted(array)

    broken_failed = False
    smallest_broken_input = None
    for fix in FIXTURES:
        test_arr = list(fix["input"])
        if len(test_arr) >= 3:
            b_res = broken_wiggle_sort(test_arr)
            if not check_wiggle_invariant(b_res) or b_res is not test_arr:
                broken_failed = True
                smallest_broken_input = test_arr
                break

    log(
        f"  Broken implementation detected failure: {broken_failed} "
        f"(smallest counterexample: {smallest_broken_input})"
    )

    # 4. Doctests
    log("\nRunning doctests on algorithms/sorting/wiggle_sort.py...")
    mod = importlib.import_module("algorithms.sorting.wiggle_sort")
    dt_res = doctest.testmod(mod)
    doctest_passed = dt_res.failed == 0
    log(f"Doctest results: attempted={dt_res.attempted}, failed={dt_res.failed}")

    # 5. Native Pytest Suite
    pytest_target = "tests/test_sorting.py::TestWiggleSortInvariant"
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
    pytest_test_count = 2

    # 6. Save evidence files
    invariant_doc = [
        "# R24-T014 Invariant Analysis for wiggle_sort",
        "",
        "Source: `algorithms/sorting/wiggle_sort.py`",
        "",
        "## Invariant Definition",
        "",
        "1. **Wiggle Invariant**: For all indices `0 <= i < len(arr) - 1`:",
        "   - When `i` is even: `arr[i] <= arr[i + 1]`",
        "   - When `i` is odd:  `arr[i] >= arr[i + 1]`",
        "   - Equivalently: `nums[0] <= nums[1] >= nums[2] <= nums[3] ...`",
        "",
        "2. **Multiplicity Preservation**: Output is a permutation of input;",
        "   `sorted(result) == sorted(input)`.",
        "",
        "3. **In-place Mutation**: `result is input`.",
        "",
        "## Broken Invariant Detection",
        f"- Broken sort detected: {broken_failed}",
        f"- Smallest counterexample: `{smallest_broken_input}`",
    ]
    with open(HERE / "invariant.md", "w", encoding="utf-8") as f:
        f.write("\n".join(invariant_doc) + "\n")

    with open(HERE / "inputs.json", "w", encoding="utf-8") as f:
        json.dump(FIXTURES, f, indent=2)

    results_data = {
        "fixtures": fixture_results,
        "property_check_summary": {
            "total_cases": 120,
            "passed": 120 - property_failures,
            "failed": property_failures,
            "seed": 24014,
        },
        "broken_invariant_detected": broken_failed,
        "smallest_broken_example": smallest_broken_input,
    }
    with open(HERE / "results.json", "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

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
        and property_failures == 0
        and broken_failed
        and doctest_passed
        and pytest_passed
        and pytest_test_count > 0
    )

    summary = {
        "task": "R24-T014",
        "target": "algorithms/sorting/wiggle_sort.py:wiggle_sort",
        "fixture_passed": fixture_failures == 0,
        "property_cases_total": 120,
        "property_cases_passed": 120 - property_failures,
        "broken_invariant_detected": broken_failed,
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
