"""Focused check runner for R24-T002 (factorial boundary cases).

Verifies the supported boundaries and contracts for ``factorial`` in
``algorithms/math/factorial.py``.

Boundary test cases:
- Lower boundary: n=0 -> 1
- Minimal positive boundary: n=1 -> 1
- Interior values: n=2 -> 2, n=5 -> 120
- Modular boundary: n=5, mod=10 -> 0; n=5, mod=7 -> 1
- Unsupported boundary values: n=-1 -> raises ValueError; mod=0 -> raises ValueError

Saves verification evidence into ``work/R24-T002/``:
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

from algorithms.math.factorial import factorial


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T002: factorial boundary cases")
    log("=" * 60)

    # 1. Native unittest execution
    test_target = "tests.test_math.TestFactorial"
    cmd = [sys.executable, "-m", "unittest", "-v", test_target]
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/math/factorial.py...")
    mod = importlib.import_module("algorithms.math.factorial")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct boundary checks
    boundary_cases = [
        {
            "id": "lower_boundary_zero",
            "description": "Smallest supported domain boundary: 0! = 1",
            "n": 0,
            "mod": None,
            "expected": 1,
            "should_raise": False,
        },
        {
            "id": "successor_boundary_one",
            "description": "Smallest strictly positive boundary: 1! = 1",
            "n": 1,
            "mod": None,
            "expected": 1,
            "should_raise": False,
        },
        {
            "id": "interior_value_two",
            "description": "First nontrivial recursive step: 2! = 2",
            "n": 2,
            "mod": None,
            "expected": 2,
            "should_raise": False,
        },
        {
            "id": "interior_value_five",
            "description": "Specified fixture interior value: 5! = 120",
            "n": 5,
            "mod": None,
            "expected": 120,
            "should_raise": False,
        },
        {
            "id": "modular_boundary_exact_multiple",
            "description": "Modulo boundary where 5! (120) % 10 = 0",
            "n": 5,
            "mod": 10,
            "expected": 0,
            "should_raise": False,
        },
        {
            "id": "modular_boundary_coprime",
            "description": "Modulo boundary where 5! (120) % 7 = 1",
            "n": 5,
            "mod": 7,
            "expected": 1,
            "should_raise": False,
        },
        {
            "id": "unsupported_negative_n",
            "description": "Directly below lower boundary: n=-1 raises ValueError",
            "n": -1,
            "mod": None,
            "expected": "ValueError",
            "should_raise": True,
        },
        {
            "id": "unsupported_zero_mod",
            "description": "Directly below modular boundary: mod=0 raises ValueError",
            "n": 5,
            "mod": 0,
            "expected": "ValueError",
            "should_raise": True,
        },
    ]

    inputs_record = []
    results_record = []
    all_passed = True

    for item in boundary_cases:
        inputs_record.append({
            "id": item["id"],
            "description": item["description"],
            "n": item["n"],
            "mod": item["mod"],
        })

        if item["should_raise"]:
            try:
                factorial(item["n"], item["mod"])
                actual = "No exception"
                passed = False
            except ValueError:
                actual = "ValueError"
                passed = True
            except Exception as e:
                actual = type(e).__name__
                passed = False
        else:
            try:
                actual = factorial(item["n"], item["mod"])
                passed = (actual == item["expected"])
            except Exception as e:
                actual = f"Error: {e}"
                passed = False

        results_record.append({
            "id": item["id"],
            "description": item["description"],
            "expected": item["expected"],
            "actual": actual,
            "passed": passed,
        })

        if not passed:
            all_passed = False
            log(f"Assertion FAILED for {item['id']}: expected {item['expected']}, got {actual}")
        else:
            log(f"Assertion PASSED for {item['id']}: n={item['n']}, mod={item['mod']} -> {actual}")

    # 4. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T002",
        "module": "algorithms.math.factorial",
        "total_boundary_cases": len(boundary_cases),
        "passed_boundary_cases": sum(1 for r in results_record if r["passed"]),
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
    log("ALL CHECKS PASSED FOR R24-T002")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
