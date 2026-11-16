"""Focused check runner for R24-T003 (can_attend_meetings independent reference comparison).

Compares ``can_attend_meetings`` from ``algorithms/sorting/meeting_rooms.py``
against an independent pairwise intersection reference oracle across 21 test inputs.

Saves verification evidence to ``work/R24-T003/``:
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

from algorithms.sorting.meeting_rooms import Interval, can_attend_meetings


def reference_oracle(intervals: list[Interval]) -> bool:
    """Independent pairwise intersection checker (does not sort)."""
    n = len(intervals)
    for i in range(n):
        for j in range(i + 1, n):
            # Overlap occurs if max(start_i, start_j) < min(end_i, end_j)
            if max(intervals[i].start, intervals[j].start) < min(intervals[i].end, intervals[j].end):
                return False
    return True


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T003: can_attend_meetings")
    log("=" * 60)

    # 1. Native unittest execution
    test_target = "tests.test_sorting.TestMeetingRooms"
    cmd = [sys.executable, "-m", "unittest", "-v", test_target]
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/sorting/meeting_rooms.py...")
    mod = importlib.import_module("algorithms.sorting.meeting_rooms")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Reference oracle comparison across >= 20 inputs
    test_cases = [
        {"id": "empty", "intervals": []},
        {"id": "single", "intervals": [Interval(1, 2)]},
        {"id": "fixture_3_1_2", "intervals": [Interval(3, 4), Interval(1, 2), Interval(2, 3)]},
        {"id": "fixture_ordered_1_2_3", "intervals": [Interval(1, 2), Interval(2, 3), Interval(3, 4)]},
        {"id": "fixture_reversed_3_2_1", "intervals": [Interval(3, 4), Interval(2, 3), Interval(1, 2)]},
        {"id": "fixture_multiplicity_2_2_1", "intervals": [Interval(2, 3), Interval(2, 4), Interval(1, 2)]},
        {"id": "touching_boundary_pair", "intervals": [Interval(1, 2), Interval(2, 3)]},
        {"id": "overlapping_pair", "intervals": [Interval(1, 3), Interval(2, 4)]},
        {"id": "touching_three", "intervals": [Interval(0, 5), Interval(5, 10), Interval(10, 15)]},
        {"id": "enclosed_interval", "intervals": [Interval(0, 10), Interval(2, 3), Interval(11, 12)]},
        {"id": "unordered_touching", "intervals": [Interval(10, 20), Interval(0, 5), Interval(5, 10)]},
        {"id": "nested_overlap", "intervals": [Interval(1, 10), Interval(2, 5)]},
        {"id": "gapped_four_ordered", "intervals": [Interval(1, 2), Interval(3, 4), Interval(5, 6), Interval(7, 8)]},
        {"id": "gapped_four_reversed", "intervals": [Interval(7, 8), Interval(5, 6), Interval(3, 4), Interval(1, 2)]},
        {"id": "overlap_in_middle", "intervals": [Interval(1, 4), Interval(2, 3), Interval(5, 6)]},
        {"id": "disjoint_intervals", "intervals": [Interval(2, 6), Interval(8, 10), Interval(15, 18)]},
        {"id": "consecutive_touching_chain", "intervals": [Interval(1, 5), Interval(5, 6), Interval(6, 7), Interval(7, 8)]},
        {"id": "partial_overlap_two", "intervals": [Interval(1, 5), Interval(4, 6)]},
        {"id": "unit_chain_four", "intervals": [Interval(0, 1), Interval(1, 2), Interval(2, 3), Interval(3, 4)]},
        {"id": "unit_overlap_two", "intervals": [Interval(0, 2), Interval(1, 3)]},
        {"id": "large_container_overlap", "intervals": [Interval(1, 100), Interval(50, 60)]},
    ]

    inputs_record = []
    results_record = []
    all_passed = True

    for item in test_cases:
        intervals = item["intervals"]
        serializable_input = [[iv.start, iv.end] for iv in intervals]
        inputs_record.append({
            "id": item["id"],
            "intervals": serializable_input,
        })

        input_copy = [Interval(iv.start, iv.end) for iv in intervals]
        actual = can_attend_meetings(input_copy)
        expected = reference_oracle(intervals)
        mutation_detected = [[iv.start, iv.end] for iv in input_copy] != serializable_input
        passed = (actual == expected) and not mutation_detected

        results_record.append({
            "id": item["id"],
            "intervals": serializable_input,
            "expected_oracle": expected,
            "actual": actual,
            "passed": passed,
            "mutation_detected": mutation_detected,
        })

        if not passed:
            all_passed = False
            log(f"FAILED for {item['id']}: expected {expected}, got {actual}")
        else:
            log(f"PASSED for {item['id']}: {serializable_input} -> {actual} (matches oracle)")

    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T003",
        "module": "algorithms.sorting.meeting_rooms",
        "total_cases": len(test_cases),
        "passed_cases": sum(1 for r in results_record if r["passed"]),
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
    log("ALL CHECKS PASSED FOR R24-T003")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
