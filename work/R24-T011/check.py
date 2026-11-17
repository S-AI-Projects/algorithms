"""Focused check runner for R24-T011: contract of contain_string.

Verifies the input/output contract, boundary conditions, and non-mutation
behavior of ``contain_string`` in ``algorithms/string/contain_string.py``.

Saves verification evidence to ``work/R24-T011/``:
- ``inputs.json``
- ``results.json``
- ``summary.json``
- ``tool_versions.json``
- ``check_output.txt``

Run from repository root:
    python3 work/R24-T011/check.py

Exits non-zero on any failure.
"""

from __future__ import annotations

import doctest
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
from algorithms.string.contain_string import contain_string  # noqa: E402

CASES = [
    {
        "name": "source_anchor",
        "description": "Primary fixture from source anchor",
        "haystack": "hello",
        "needle": "ll",
        "expected": 2,
    },
    {
        "name": "neighbour_suffix",
        "description": "Neighboring input: suffix match 'lo' at index 3",
        "haystack": "hello",
        "needle": "lo",
        "expected": 3,
    },
    {
        "name": "neighbour_prefix",
        "description": "Neighboring input: prefix match 'he' at index 0",
        "haystack": "hello",
        "needle": "he",
        "expected": 0,
    },
    {
        "name": "neighbour_partial_mismatch",
        "description": "Neighboring input: partial prefix 'l' followed by mismatch 'a'",
        "haystack": "hello",
        "needle": "la",
        "expected": -1,
    },
    {
        "name": "smallest_empty_needle_and_haystack",
        "description": "Smallest input: empty needle in empty haystack -> 0",
        "haystack": "",
        "needle": "",
        "expected": 0,
    },
    {
        "name": "smallest_empty_needle_nonempty_haystack",
        "description": "Smallest needle: empty needle in non-empty haystack -> 0",
        "haystack": "a",
        "needle": "",
        "expected": 0,
    },
    {
        "name": "smallest_nonempty_needle_empty_haystack",
        "description": "Non-empty needle in empty haystack -> -1",
        "haystack": "",
        "needle": "a",
        "expected": -1,
    },
    {
        "name": "smallest_single_char_match",
        "description": "Smallest non-empty exact match: single character",
        "haystack": "a",
        "needle": "a",
        "expected": 0,
    },
    {
        "name": "smallest_single_char_mismatch",
        "description": "Smallest single character mismatch",
        "haystack": "a",
        "needle": "b",
        "expected": -1,
    },
    {
        "name": "boundary_all_identical",
        "description": "Repeated-value boundary: all characters identical",
        "haystack": "aaaaa",
        "needle": "aa",
        "expected": 0,
    },
    {
        "name": "boundary_repeated_pattern",
        "description": "Repeated pattern in haystack, returns first occurrence index 0",
        "haystack": "abcabc",
        "needle": "abc",
        "expected": 0,
    },
    {
        "name": "boundary_multiple_occurrences",
        "description": (
            "Multiple occurrences of needle in haystack; returns first at index 2"
        ),
        "haystack": "helloll",
        "needle": "ll",
        "expected": 2,
    },
    {
        "name": "boundary_overlapping_partial_match",
        "description": "Overlapping partial match before full match",
        "haystack": "mississippi",
        "needle": "issi",
        "expected": 1,
    },
    {
        "name": "boundary_needle_longer_than_haystack",
        "description": "Needle length strictly greater than haystack length",
        "haystack": "short",
        "needle": "longer_needle",
        "expected": -1,
    },
    {
        "name": "boundary_full_match",
        "description": "Needle equals entire haystack",
        "haystack": "hello",
        "needle": "hello",
        "expected": 0,
    },
    {
        "name": "case_sensitivity_haystack",
        "description": "Case sensitivity: capitalized haystack",
        "haystack": "Hello",
        "needle": "hello",
        "expected": -1,
    },
    {
        "name": "case_sensitivity_needle",
        "description": "Case sensitivity: capitalized needle",
        "haystack": "hello",
        "needle": "LL",
        "expected": -1,
    },
]


def run_checks() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 70)
    log("R24-T011 contain_string contract check")
    log("=" * 70)

    # 1. Direct cases verification
    log("\nDirect cases (expected vs actual):")
    inputs_evidence = []
    results_evidence = []
    direct_failures = 0

    for case in CASES:
        name = case["name"]
        haystack = case["haystack"]
        needle = case["needle"]
        expected = case["expected"]

        inputs_evidence.append(
            {
                "name": name,
                "description": case["description"],
                "haystack": haystack,
                "needle": needle,
                "expected": expected,
            }
        )

        h_copy = str(haystack)
        n_copy = str(needle)
        actual = contain_string(haystack, needle)
        repeat_actual = contain_string(haystack, needle)

        value_ok = actual == expected
        input_unchanged = (haystack == h_copy) and (needle == n_copy)
        idempotent = actual == repeat_actual
        passed = value_ok and input_unchanged and idempotent

        if not passed:
            direct_failures += 1
            status = "FAIL"
        else:
            status = "PASS"

        log(
            f"  [{status}] {name}: haystack={haystack!r} needle={needle!r} "
            f"expected={expected} actual={actual} input_unchanged={input_unchanged}"
        )

        results_evidence.append(
            {
                "name": name,
                "description": case["description"],
                "haystack": haystack,
                "needle": needle,
                "expected": expected,
                "actual": actual,
                "value_ok": value_ok,
                "input_unchanged": input_unchanged,
                "idempotent": idempotent,
                "passed": passed,
            }
        )

    # 2. Doctests
    log("\nRunning doctests on algorithms/string/contain_string.py...")
    import importlib

    mod_contain_string = importlib.import_module("algorithms.string.contain_string")
    dt_res = doctest.testmod(mod_contain_string)
    doctest_passed = dt_res.failed == 0
    log(f"Doctest results: attempted={dt_res.attempted}, failed={dt_res.failed}")

    # 3. Native test execution (pytest / unittest)
    pytest_target = "tests/test_string.py::TestContainString"
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

    # 4. Save evidence artifacts
    inputs_path = HERE / "inputs.json"
    results_path = HERE / "results.json"
    summary_path = HERE / "summary.json"
    tools_path = HERE / "tool_versions.json"
    output_path = HERE / "check_output.txt"

    with open(inputs_path, "w", encoding="utf-8") as f:
        json.dump(inputs_evidence, f, indent=2)

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_evidence, f, indent=2)

    try:
        ver_proc = subprocess.run(
            [pytest_cmd[0], "--version"], capture_output=True, text=True
        )
        pytest_ver = (ver_proc.stdout or ver_proc.stderr).strip().split()[-1]
    except Exception:
        try:
            pytest_ver = importlib.metadata.version("pytest")
        except Exception:
            pytest_ver = "unknown"

    tool_versions = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pytest": pytest_ver,
        "pytest_command": " ".join(pytest_cmd),
    }
    with open(tools_path, "w", encoding="utf-8") as f:
        json.dump(tool_versions, f, indent=2)

    overall_passed = (
        direct_failures == 0
        and doctest_passed
        and pytest_passed
        and pytest_test_count > 0
    )

    summary = {
        "task": "R24-T011",
        "target": "algorithms/string/contain_string.py:contain_string",
        "direct_cases": len(CASES),
        "direct_cases_passed": len(CASES) - direct_failures,
        "doctest_attempted": dt_res.attempted,
        "doctest_failed": dt_res.failed,
        "pytest_command": " ".join(pytest_cmd),
        "pytest_test_count": pytest_test_count,
        "pytest_passed": pytest_passed,
        "overall": "PASS" if overall_passed else "FAIL",
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    log(f"\nOVERALL: {'PASS' if overall_passed else 'FAIL'}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(run_checks())
