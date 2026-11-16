"""Focused check runner for R24-T038 (has_alternative_bit edge branch).

Exercises the absent-result branch of ``has_alternative_bit``: input ``0``
has no set bits, so ``while number:`` (line 34) never runs and control
reaches the trailing ``return True`` at line 43. Runs the project's
native unittest check with ``sys.stdout``/``sys.stderr`` captured and
writes task artifacts into ``work/R24-T038/``. Exits non-zero on failure.
"""

from __future__ import annotations

import contextlib
import doctest
import importlib
import io
import json
import os
import platform
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)

TEST_NAMES = [
    "tests.test_bit_manipulation.TestSuite.test_has_alternative_bit",
    "tests.test_bit_manipulation.TestSuite.test_has_alternative_bit_fast",
    "tests.test_bit_manipulation.TestSuite.test_has_alternative_bit_empty_input",
]
COMMAND = [sys.executable, "-m", "unittest", "-v"] + TEST_NAMES

FIXTURES = [
    # Source anchors from the module docstrings.
    {"name": "anchor_5", "function": "has_alternative_bit", "input": 5,
     "expected": True, "branch": "inner else return True (line 41)"},
    {"name": "anchor_7", "function": "has_alternative_bit", "input": 7,
     "expected": False, "branch": "return False (line 39)"},
    {"name": "anchor_fast_5", "function": "has_alternative_bit_fast",
     "input": 5, "expected": True, "branch": "O(1) mask return (line 63)"},
    # Neighboring supported input derived independently: 6 = 0b110 has
    # adjacent equal bits (1,1), so it is not alternating -> False.
    {"name": "neighbor_6", "function": "has_alternative_bit", "input": 6,
     "expected": False, "branch": "return False (line 39)"},
    # Absent-result / empty case: 0 has no bits; the while loop is skipped
    # and the trailing `return True` at line 43 is reached.
    {"name": "empty_zero", "function": "has_alternative_bit", "input": 0,
     "expected": True, "branch": "trailing return True (line 43)"},
]

# Ordinary valid calls that must still succeed after the boundary case.
POST_FAILURE_CALLS = [
    {"function": "has_alternative_bit", "input": 5, "expected": True},
    {"function": "has_alternative_bit", "input": 7, "expected": False},
    {"function": "has_alternative_bit_fast", "input": 5, "expected": True},
]


def write_json(name, payload):
    path = os.path.join(WORK_DIR, name)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    return path


def git_version():
    try:
        return subprocess.check_output(
            ["git", "--version"], cwd=REPO_ROOT, text=True
        ).strip()
    except Exception as exc:  # pragma: no cover - defensive
        return f"unavailable: {exc}"


def run_fixture_cases():
    module = importlib.import_module("algorithms.bit_manipulation.has_alternative_bit")
    rows = []
    for case in FIXTURES + [
        {**c, "name": "post_failure_" + c["function"] + "_" + str(c["input"])}
        for c in POST_FAILURE_CALLS
    ]:
        func = getattr(module, case["function"])
        actual = func(case["input"])
        rows.append({
            "name": case["name"],
            "function": case["function"],
            "input": case["input"],
            "expected": case["expected"],
            "actual": actual,
            "branch": case.get("branch"),
            "passed": actual == case["expected"] and actual is case["expected"],
        })
    return rows


def run_native_tests():
    """Run the focused unittest selection with external I/O mocked."""
    out, err = io.StringIO(), io.StringIO()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in TEST_NAMES:
        suite.addTests(loader.loadTestsFromName(name))
    runner = unittest.TextTestRunner(stream=out, verbosity=2)
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = runner.run(suite)
    return result, out.getvalue() + err.getvalue()


def run_doctest():
    module = importlib.import_module("algorithms.bit_manipulation.has_alternative_bit")
    finder = doctest.DocTestFinder()
    runner = doctest.DocTestRunner(verbose=False)
    for test in finder.find(module, module.__name__):
        runner.run(test)
    return runner.summarize()


def _pytest_available():
    try:
        importlib.import_module("pytest")
        return True
    except ImportError:
        return False


def main():
    fixture_rows = run_fixture_cases()
    test_result, test_log = run_native_tests()
    doctest_summary = run_doctest()

    failures = [row["name"] for row in fixture_rows if not row["passed"]]
    test_failures = len(test_result.failures) + len(test_result.errors)
    doctest_failed = doctest_summary.failed

    inputs = {
        "task": "R24-T038",
        "module": "algorithms/bit_manipulation/has_alternative_bit.py",
        "public_functions": [
            "has_alternative_bit(number: int) -> bool",
            "has_alternative_bit_fast(number: int) -> bool",
        ],
        "contract": {
            "inputs": "int (documented as positive; total function, returns bool)",
            "result": "True iff every pair of adjacent bits differs",
            "mutation": "none; pure function, no caller-owned state",
            "dependencies": ["none beyond builtins"],
            "descending_interface": False,
        },
        "target_branch": {
            "name": "absent-result / empty bit pattern",
            "location": "trailing `return True` at line 43, reached when "
                        "`while number:` (line 34) is skipped for input 0",
            "smallest_input": 0,
        },
        "fixtures": FIXTURES,
        "post_failure_calls": POST_FAILURE_CALLS,
        "native_check_command": COMMAND,
    }

    results = {
        "fixtures": fixture_rows,
        "unittest": {
            "command": COMMAND,
            "tests_run": test_result.testsRun,
            "failures": test_failures,
            "passed": test_failures == 0,
        },
        "doctest": {
            "attempted": doctest_summary.attempted,
            "failed": doctest_failed,
            "passed": doctest_failed == 0,
        },
    }

    versions = {
        "python": sys.version.split()[0],
        "python_full": sys.version,
        "platform": platform.platform(),
        "os": platform.system(),
        "git": git_version(),
        "unittest": unittest.__name__,
        "doctest": doctest.__name__,
        "pytest_configured": _pytest_available(),
    }

    ok = not failures and test_failures == 0 and doctest_failed == 0
    summary = {
        "task": "R24-T038",
        "status": "PASS" if ok else "FAIL",
        "fixture_failures": failures,
        "unittest": results["unittest"],
        "doctest": results["doctest"],
        "artifacts": [
            "inputs.json", "results.json", "tool_versions.json",
            "summary.json", "check_output.txt",
        ],
    }

    write_json("inputs.json", inputs)
    write_json("results.json", results)
    write_json("tool_versions.json", versions)
    write_json("summary.json", summary)

    log_path = os.path.join(WORK_DIR, "check_output.txt")
    with open(log_path, "w") as fh:
        fh.write("$ " + " ".join(COMMAND) + "\n\n")
        fh.write(test_log)
        fh.write("\nFixture results:\n")
        for row in fixture_rows:
            fh.write(
                f"  {row['name']}: {row['function']}({row['input']}) "
                f"expected={row['expected']} actual={row['actual']} "
                f"passed={row['passed']}\n"
            )
        fh.write(f"\nDoctest: attempted={doctest_summary.attempted} "
                 f"failed={doctest_summary.failed}\n")
        fh.write(f"Overall: {'PASS' if ok else 'FAIL'}\n")

    print(test_log)
    print(f"check.py: {'PASS' if ok else 'FAIL'} "
          f"(fixtures={len(fixture_rows) - len(failures)}/{len(fixture_rows)}, "
          f"unittest_failures={test_failures}, doctest_failed={doctest_failed})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
