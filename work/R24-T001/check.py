"""Focused check runner for R24-T001 (max_ones_index contract).

Verifies the input/output contract, boundary conditions, and non-mutation
behavior of ``max_ones_index`` in ``algorithms/array/max_ones_index.py``.

Saves verification evidence to ``work/R24-T001/``:
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
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from algorithms.array.max_ones_index import max_ones_index


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T001: max_ones_index")
    log("=" * 60)

    # 1. Native unittest execution
    test_target = "tests.test_array.TestMaxOnesIndex"
    cmd = [sys.executable, "-m", "unittest", "-v", test_target]
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/array/max_ones_index.py...")
    mod = importlib.import_module("algorithms.array.max_ones_index")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct fixture & boundary assertions
    fixtures = [
        {
            "id": "source_anchor",
            "description": "Primary fixture from source anchor with two zeros at indices 3 and 9",
            "input": [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            "expected": 3,
        },
        {
            "id": "neighbor_extended_trailing_ones",
            "description": "Neighboring input where extending trailing ones makes index 9 optimal (5+1+6=12 ones vs 3+1+5=9)",
            "input": [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            "expected": 9,
        },
        {
            "id": "smallest_empty",
            "description": "Smallest supported input: empty list",
            "input": [],
            "expected": -1,
        },
        {
            "id": "single_zero",
            "description": "Smallest input containing a zero",
            "input": [0],
            "expected": 0,
        },
        {
            "id": "single_one",
            "description": "Smallest input containing no zero",
            "input": [1],
            "expected": -1,
        },
        {
            "id": "repeated_boundary_all_zeros",
            "description": "Repeated-value boundary: all zeros",
            "input": [0, 0, 0],
            "expected": 0,
        },
        {
            "id": "adjacent_zeros",
            "description": "Adjacent zeros: [1, 0, 0, 1]",
            "input": [1, 0, 0, 1],
            "expected": 1,
        },
    ]

    inputs_record = []
    results_record = []
    all_passed = True

    for item in fixtures:
        raw_input = item["input"]
        input_copy = list(raw_input)
        actual = max_ones_index(input_copy)
        mutation_detected = input_copy != raw_input
        passed = (actual == item["expected"]) and not mutation_detected

        inputs_record.append({
            "id": item["id"],
            "description": item["description"],
            "input": raw_input,
        })

        results_record.append({
            "id": item["id"],
            "description": item["description"],
            "expected": item["expected"],
            "actual": actual,
            "passed": passed,
            "mutation_detected": mutation_detected,
        })

        if not passed:
            all_passed = False
            log(f"Assertion FAILED for {item['id']}: expected {item['expected']}, got {actual}, mutated={mutation_detected}")
        else:
            log(f"Assertion PASSED for {item['id']}: {raw_input} -> {actual} (expected {item['expected']})")

    # 4. Input immutability check
    sample = [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1]
    sample_snapshot = list(sample)
    ret = max_ones_index(sample)
    if sample != sample_snapshot:
        all_passed = False
        log("FAILED: Input list was mutated in-place by max_ones_index")

    # 5. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T001",
        "module": "algorithms.array.max_ones_index",
        "total_fixtures": len(fixtures),
        "passed_fixtures": sum(1 for r in results_record if r["passed"]),
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
    log("ALL CHECKS PASSED FOR R24-T001")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
