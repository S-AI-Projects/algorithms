"""Focused check runner for R24-T005 (Repeatable verification for insertion_sort).

Verifies the deterministic execution, repeatability, and state isolation of
``insertion_sort`` in ``algorithms/sorting/insertion_sort.py``:
- Fixtures: [3, 1, 2], [2, 2, 1], [1, 2, 3], [3, 2, 1], [], [42]
- Repeatability check: identical inputs produce identical outputs across multiple runs
- State isolation check: intermediate executions do not pollute subsequent sorting runs
- In-place mutation contract: return value is the exact same list object instance
- External dependency isolation: verified with external I/O mocks

Saves verification evidence into ``work/R24-T005/``:
- ``inputs.json``
- ``results.json``
- ``summary.json``
- ``tool_versions.json``
- ``check_output.txt``

Exits non-zero on any failure.
"""

from __future__ import annotations

import doctest
import importlib
import json
import os
import platform
import subprocess
import sys
from unittest.mock import patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from algorithms.sorting.insertion_sort import insertion_sort


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T005: insertion_sort determinism")
    log("=" * 60)

    # 1. Native unittest execution
    test_targets = [
        "tests.test_sorting.TestSuite.test_insertion_sort",
        "tests.test_sorting.TestSuite.test_insertion_sort_repeatability_and_fixtures",
        "tests.test_sorting.TestSuite.test_insertion_sort_in_place_identity",
    ]
    cmd = [sys.executable, "-m", "unittest", "-v"] + test_targets
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/sorting/insertion_sort.py...")
    mod = importlib.import_module("algorithms.sorting.insertion_sort")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct fixture verification
    fixtures = [
        {"id": "fixture_3_1_2", "input": [3, 1, 2], "expected": [1, 2, 3]},
        {"id": "fixture_2_2_1", "input": [2, 2, 1], "expected": [1, 2, 2]},
        {"id": "fixture_ordered_1_2_3", "input": [1, 2, 3], "expected": [1, 2, 3]},
        {"id": "fixture_reversed_3_2_1", "input": [3, 2, 1], "expected": [1, 2, 3]},
        {"id": "smallest_empty", "input": [], "expected": []},
        {"id": "smallest_single", "input": [42], "expected": [42]},
        {"id": "negative_and_duplicates", "input": [5, -2, 0, 5, -2], "expected": [-2, -2, 0, 5, 5]},
    ]

    inputs_record = []
    results_record = []
    all_passed = True

    # Run with external I/O mocked to prove complete dependency isolation
    with patch("builtins.open") as mock_open:
        for f in fixtures:
            inp = list(f["input"])
            inputs_record.append({"id": f["id"], "input": f["input"]})
            actual = insertion_sort(inp)
            passed = (actual == f["expected"]) and (actual is inp)
            results_record.append({
                "id": f["id"],
                "expected": f["expected"],
                "actual": actual,
                "in_place": actual is inp,
                "passed": passed,
            })
            if not passed:
                all_passed = False
                log(f"FAILED for {f['id']}: expected {f['expected']}, got {actual}")
            else:
                log(f"PASSED for {f['id']}: {f['input']} -> {actual}")

        # Assert no external I/O was invoked
        if mock_open.called:
            all_passed = False
            log("FAILED: external I/O mock was invoked by insertion_sort")
        else:
            log("External I/O isolation confirmed: zero I/O operations performed")

    # 4. Repeatability across intermediate states
    seq1 = insertion_sort([3, 1, 2])
    inter = insertion_sort([99, -1, 50, 0])
    seq2 = insertion_sort([3, 1, 2])
    repeatability_verified = (seq1 == [1, 2, 3]) and (seq2 == [1, 2, 3]) and (inter == [-1, 0, 50, 99])
    if not repeatability_verified:
        all_passed = False
        log("FAILED: Repeatability check failed across intermediate executions")
    else:
        log("Repeatability verified: identical results produced before and after independent execution")

    # 5. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T005",
        "module": "algorithms.sorting.insertion_sort",
        "total_fixtures": len(fixtures),
        "passed_fixtures": sum(1 for r in results_record if r["passed"]),
        "repeatability_verified": repeatability_verified,
        "external_io_isolated": not mock_open.called,
        "doctest_passed": doctest_res.failed == 0,
        "unittest_passed": proc.returncode == 0,
        "all_passed": all_passed,
    }

    with open(os.path.join(WORK_DIR, "inputs.json"), "w") as f:
        json.dump(inputs_record, f, indent=2)

    with open(os.path.join(WORK_DIR, "results.json"), "w") as f:
        json.dump(results_record, f, indent=2)

    with open(os.path.join(WORK_DIR, "tool_versions.json"), "w") as f:
        json.dump(tool_versions, f, indent=2)

    with open(os.path.join(WORK_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    with open(os.path.join(WORK_DIR, "check_output.txt"), "w") as f:
        f.write("\n".join(log_lines) + "\n")

    if not all_passed:
        log("FAILED: One or more assertions failed.")
        return 1

    log("=" * 60)
    log("ALL CHECKS PASSED FOR R24-T005")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
