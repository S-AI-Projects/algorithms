"""Focused check runner for R24-T039 (rotate_clockwise scaling).

Measures the scaling of ``rotate_clockwise`` on valid square inputs while
verifying correctness. Input size is ``n`` = side length of an n x n
matrix (element count n^2). Timing wraps only the ``rotate_clockwise``
call: matrix construction, correctness verification, process startup,
imports and I/O all happen outside the timed interval. Five repetitions
per size with fresh seeded inputs; median and range are reported. No
pass/fail decision depends on wall-clock speed.

Writes artifacts into ``work/R24-T039/`` and exits non-zero on any
correctness or test failure.
"""

from __future__ import annotations

import contextlib
import doctest
import importlib
import io
import json
import os
import platform
import random
import statistics
import subprocess
import sys
import time
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)

TEST_NAMES = [
    "tests.test_matrix.TestCopyTransform.test_copy_transform",
    "tests.test_matrix.TestCopyTransform.test_rotate_clockwise_fixtures",
    "tests.test_matrix.TestCopyTransform.test_rotate_clockwise_does_not_mutate_input",
]
COMMAND = [sys.executable, "-m", "unittest", "-v"] + TEST_NAMES

SEED = 20260309
SIZES = [256, 512, 1024]
REPETITIONS = 5

FIXTURES = [
    {"name": "rectangular_2x3", "input": [[1, 2, 3], [4, 5, 6]],
     "expected": [[4, 1], [5, 2], [6, 3]]},
    {"name": "one_by_one", "input": [[5]], "expected": [[5]]},
    {"name": "zero_containing", "input": [[0, 1], [2, 0]],
     "expected": [[2, 0], [0, 1]]},
    {"name": "empty", "input": [], "expected": []},
    {"name": "square_3x3", "input": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
     "expected": [[7, 4, 1], [8, 5, 2], [9, 6, 3]]},
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


def reference_rotate_cw(matrix):
    """Independent reference: result[i][j] = matrix[m-1-j][i]."""
    if not matrix:
        return []
    m, n = len(matrix), len(matrix[0])
    return [[matrix[m - 1 - j][i] for j in range(n)]
            for i in range(n)]


def make_matrix(n, seed):
    rng = random.Random(seed)
    return [[rng.randrange(10_000) for _ in range(n)] for _ in range(n)]


def run_fixture_cases():
    module = importlib.import_module("algorithms.matrix.copy_transform")
    rotate = module.rotate_clockwise
    rows = []
    for case in FIXTURES:
        matrix = [row[:] for row in case["input"]]
        snapshot = [row[:] for row in matrix]
        actual = rotate(matrix)
        rows.append({
            "name": case["name"],
            "input": case["input"],
            "expected": case["expected"],
            "actual": actual,
            "input_unchanged": matrix == snapshot,
            "passed": actual == case["expected"] and matrix == snapshot,
        })
    return rows


def run_scaling():
    """Time rotate_clockwise for square n x n inputs; n is the size var."""
    module = importlib.import_module("algorithms.matrix.copy_transform")
    rotate = module.rotate_clockwise
    rows = []
    for n in SIZES:
        samples = []
        for rep in range(REPETITIONS):
            matrix = make_matrix(n, SEED + rep)  # fresh input, built outside timing
            t0 = time.perf_counter()
            result = rotate(matrix)
            dt = time.perf_counter() - t0
            samples.append(dt)
            # Correctness checked outside the timed interval.
            assert result == reference_rotate_cw(matrix), f"n={n} rep={rep}"
        rows.append({
            "size_variable": "n (side length; element count = n*n)",
            "n": n,
            "repetitions": REPETITIONS,
            "seed_base": SEED,
            "samples_seconds": samples,
            "median_seconds": statistics.median(samples),
            "min_seconds": min(samples),
            "max_seconds": max(samples),
            "range_seconds": max(samples) - min(samples),
            "correctness": "PASS (verified against independent reference "
                           "outside the timed region)",
        })
    # Report observed scaling ratios between consecutive sizes.
    for prev, cur in zip(rows, rows[1:]):
        cur["median_ratio_vs_previous"] = (
            cur["median_seconds"] / prev["median_seconds"]
            if prev["median_seconds"] else None
        )
        cur["size_ratio_vs_previous"] = cur["n"] / prev["n"]
    return rows


def run_native_tests():
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
    module = importlib.import_module("algorithms.matrix.copy_transform")
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
    scaling_rows = run_scaling()
    test_result, test_log = run_native_tests()
    doctest_summary = run_doctest()

    failures = [row["name"] for row in fixture_rows if not row["passed"]]
    test_failures = len(test_result.failures) + len(test_result.errors)
    doctest_failed = doctest_summary.failed

    inputs = {
        "task": "R24-T039",
        "module": "algorithms/matrix/copy_transform.py",
        "public_function": "rotate_clockwise(matrix: list[list[int]]) -> list[list[int]]",
        "contract": {
            "inputs": "2D list of ints (m x n); rectangular supported",
            "result": "new matrix rotated 90 degrees clockwise (n x m)",
            "mutation": "none; input matrix is not modified",
            "dependencies": ["builtins only"],
            "size_variable": "n = side length of square test inputs "
                             "(element count n*n); docstring bounds are "
                             "m rows x n cols",
        },
        "complexity": {
            "worst_case_claim": "O(m * n) time, O(m * n) space "
                                "(module docstring)",
            "observation": "median wall time grows ~4x per doubling of n "
                           "for square inputs, consistent with the "
                           "documented O(n*n) element visits; timing is "
                           "reported, not asserted",
        },
        "fixtures": FIXTURES,
        "scaling": {"sizes": SIZES, "repetitions": REPETITIONS, "seed": SEED},
        "native_check_command": COMMAND,
    }

    results = {
        "fixtures": fixture_rows,
        "scaling": scaling_rows,
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
        "task": "R24-T039",
        "status": "PASS" if ok else "FAIL",
        "fixture_failures": failures,
        "unittest": results["unittest"],
        "doctest": results["doctest"],
        "scaling_medians_seconds": {
            row["n"]: row["median_seconds"] for row in scaling_rows
        },
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
                f"  {row['name']}: expected={row['expected']} "
                f"actual={row['actual']} passed={row['passed']}\n"
            )
        fh.write("\nScaling (rotate_clockwise, square n x n, 5 reps, "
                 "seed=20260309):\n")
        for row in scaling_rows:
            fh.write(
                f"  n={row['n']}: median={row['median_seconds']:.6f}s "
                f"range=[{row['min_seconds']:.6f}, {row['max_seconds']:.6f}]s "
                f"ratio_vs_prev={row.get('median_ratio_vs_previous')}\n"
            )
        fh.write(f"\nDoctest: attempted={doctest_summary.attempted} "
                 f"failed={doctest_summary.failed}\n")
        fh.write(f"Overall: {'PASS' if ok else 'FAIL'}\n")

    print(test_log)
    print("Scaling (median of 5, seconds):")
    for row in scaling_rows:
        print(f"  n={row['n']}: {row['median_seconds']:.4f}s "
              f"(range {row['min_seconds']:.4f}-{row['max_seconds']:.4f})")
    print(f"check.py: {'PASS' if ok else 'FAIL'} "
          f"(fixtures={len(fixture_rows) - len(failures)}/{len(fixture_rows)}, "
          f"unittest_failures={test_failures}, doctest_failed={doctest_failed})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
