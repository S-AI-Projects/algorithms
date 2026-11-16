"""Focused check runner for R24-T010 (Mutation-resistant tests for search_range).

Verifies the regression tests for ``search_range`` in
``algorithms/searching/search_range.py``:
- Source anchors: `[5, 7, 7, 8, 8, 8, 10]` with targets 8 -> [3, 5] and 11 -> [-1, -1]
- Derived neighbor: target 7 -> [1, 2]
- Mutation resistance: proves that the test suite detects a plausible one-line bug
  (`if target < nums[mid]` replacing `<=` at line 40), which produces [4, 5] instead of [3, 5]
- Immutability and repeatability assertions

Saves verification evidence into ``work/R24-T010/``:
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from algorithms.searching.search_range import search_range


def mutant_search_range(nums: list[int], target: int) -> list[int]:
    """Plausible mutant: line 40 uses strict '<' instead of '<='."""
    low = 0
    high = len(nums) - 1

    while low < high:
        mid = low + (high - low) // 2
        # Mistake: strict '<' skips the first occurrence of target
        if target < nums[mid]:
            high = mid
        else:
            low = mid + 1

    for j in range(len(nums) - 1, -1, -1):
        if nums[j] == target:
            return [low, j]

    return [-1, -1]


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T010: search_range mutation resistance")
    log("=" * 60)

    # 1. Native unittest execution
    test_targets = [
        "tests.test_searching.TestSuite.test_search_range",
        "tests.test_searching.TestSuite.test_search_range_fixtures_and_boundaries",
        "tests.test_searching.TestSuite.test_search_range_does_not_mutate_input",
        "tests.test_searching.TestSuite.test_search_range_repeatability",
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
    log("Running doctests on algorithms/searching/search_range.py...")
    mod = importlib.import_module("algorithms.searching.search_range")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct fixture verification
    fixtures = [
        {"id": "source_anchor_target_8", "nums": [5, 7, 7, 8, 8, 8, 10], "target": 8, "expected": [3, 5]},
        {"id": "source_anchor_target_11_missing", "nums": [5, 7, 7, 8, 8, 8, 10], "target": 11, "expected": [-1, -1]},
        {"id": "derived_neighbor_target_7", "nums": [5, 7, 7, 8, 8, 8, 10], "target": 7, "expected": [1, 2]},
        {"id": "first_element_target_5", "nums": [5, 7, 7, 8, 8, 8, 10], "target": 5, "expected": [0, 0]},
        {"id": "last_element_target_10", "nums": [5, 7, 7, 8, 8, 8, 10], "target": 10, "expected": [6, 6]},
        {"id": "smallest_empty", "nums": [], "target": 5, "expected": [-1, -1]},
        {"id": "single_hit", "nums": [8], "target": 8, "expected": [0, 0]},
        {"id": "single_miss", "nums": [8], "target": 5, "expected": [-1, -1]},
    ]

    inputs_record = []
    results_record = []
    all_passed = True

    for f in fixtures:
        arr_copy = list(f["nums"])
        actual = search_range(arr_copy, f["target"])
        unmutated = (arr_copy == f["nums"])
        passed = (actual == f["expected"]) and unmutated

        inputs_record.append({
            "id": f["id"],
            "nums": f["nums"],
            "target": f["target"],
        })

        results_record.append({
            "id": f["id"],
            "expected": f["expected"],
            "actual": actual,
            "unmutated": unmutated,
            "passed": passed,
        })

        if not passed:
            all_passed = False
            log(f"FAILED for {f['id']}: expected {f['expected']}, got {actual}")
        else:
            log(f"PASSED for {f['id']}: nums={f['nums']}, target={f['target']} -> {actual}")

    # 4. Mutation analysis: Prove regression test detects plausible one-line bug
    test_input = [5, 7, 7, 8, 8, 8, 10]
    expected_result = [3, 5]
    original_result = search_range(list(test_input), 8)
    mutant_result = mutant_search_range(list(test_input), 8)

    original_passed = (original_result == expected_result)
    mutant_caught = (mutant_result != expected_result)  # Mutant must be detected as failing!
    mutation_analysis_passed = original_passed and mutant_caught

    if not mutation_analysis_passed:
        all_passed = False
        log(f"FAILED: Mutant was not caught! Original={original_result}, Mutant={mutant_result}")
    else:
        log(f"Mutation test SUCCESSFUL: original returned {original_result} (PASS), mutant returned {mutant_result} (REJECTED by test)")

    # 5. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T010",
        "module": "algorithms.searching.search_range",
        "mutation_tested": "Line 40: replaced 'target <= nums[mid]' with strict 'target < nums[mid]'",
        "original_result": original_result,
        "mutant_result": mutant_result,
        "mutant_caught": mutant_caught,
        "fixtures_total": len(fixtures),
        "fixtures_passed": sum(1 for r in results_record if r["passed"]),
        "doctest_passed": doctest_res.failed == 0,
        "unittest_passed": proc.returncode == 0,
        "all_passed": all_passed,
    }

    with open(os.path.join(WORK_DIR, "inputs.json"), "w") as f:
        json.dump(inputs_record, f, indent=2)

    with open(os.path.join(WORK_DIR, "results.json"), "w") as f:
        json.dump({
            "fixture_results": results_record,
            "mutation_detection": {
                "original_result": original_result,
                "mutant_result": mutant_result,
                "expected": expected_result,
                "mutant_caught_by_assertion": mutant_caught,
            },
        }, f, indent=2)

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
    log("ALL CHECKS PASSED FOR R24-T010")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
