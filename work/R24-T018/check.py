#!/usr/bin/env python3
"""Focused check runner for R24-T018: quick_sort failure / boundary behavior.

Covers:
1. Empty list (smallest supported collection) -> early-exit path
2. Single-element input -> early-exit path
3. Fixture cases: [3,1,2], [2,2,1], already ordered, reversed
4. In-place mutation contract (same list object returned)
5. Valid call succeeds after empty no-op
6. Native pytest on tests/test_sorting.py::TestQuickSortFailureBehavior
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

qs_module = importlib.import_module("algorithms.sorting.quick_sort")
quick_sort = qs_module.quick_sort

WORK_DIR = PROJECT_ROOT / "work" / "R24-T018"
WORK_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("R24-T018: quick_sort Failure / Boundary Behavior")
    log("=" * 60)

    cases = [
        ([], []),
        ([42], [42]),
        ([3, 1, 2], [1, 2, 3]),
        ([2, 2, 1], [1, 2, 2]),
        ([1, 2, 3], [1, 2, 3]),
        ([3, 2, 1], [1, 2, 3]),
    ]

    results_data = []
    for inp, expected in cases:
        arr = list(inp)
        result = quick_sort(arr)
        assert result == expected, f"Expected {expected}, got {result} for input {inp}"
        assert result is arr, "quick_sort must return the same list object (in-place)"
        log(f"PASS: quick_sort({inp}) -> {result}")
        results_data.append({"input": inp, "expected": expected, "actual": result})

    # In-place mutation check
    original = [5, 3, 8, 1]
    saved_id = id(original)
    quick_sort(original)
    assert id(original) == saved_id, "Object identity must be preserved"
    assert original == [1, 3, 5, 8], f"Expected [1,3,5,8] got {original}"
    log("PASS: in-place mutation verified (same list object, correct order)")

    # Valid call after empty no-op
    empty: list[int] = []
    quick_sort(empty)
    normal = [3, 1, 2]
    res = quick_sort(normal)
    assert res == [1, 2, 3], f"Expected [1,2,3] got {res}"
    log("PASS: valid call succeeds after empty no-op")

    # Native test suite
    test_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "tests/test_sorting.py::TestQuickSortFailureBehavior",
    ]
    log(f"Running: {' '.join(test_cmd)}")
    result_proc = subprocess.run(
        test_cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    log(result_proc.stdout)
    if result_proc.stderr:
        log(result_proc.stderr)
    assert result_proc.returncode == 0, (
        f"Pytest failed with code {result_proc.returncode}"
    )
    log("PASS: Native pytest passed.")

    # Save evidence
    with open(WORK_DIR / "inputs.json", "w") as f:
        json.dump({"cases": cases}, f, indent=2)
    with open(WORK_DIR / "results.json", "w") as f:
        json.dump({"results": results_data}, f, indent=2)
    with open(WORK_DIR / "summary.json", "w") as f:
        json.dump(
            {
                "task": "R24-T018",
                "status": "PASS",
                "function": "quick_sort",
                "module": "algorithms.sorting.quick_sort",
                "failure_path": (
                    "_quick_sort_recursive returns immediately when first >= last"
                ),
                "cases_checked": len(cases),
                "in_place_verified": True,
                "pytest_passed": True,
            },
            f,
            indent=2,
        )

    def get_ver(pkg: str) -> str:
        try:
            return importlib.metadata.version(pkg)
        except Exception:
            return "unknown"

    with open(WORK_DIR / "tool_versions.json", "w") as f:
        json.dump(
            {
                "python": sys.version,
                "platform": platform.platform(),
                "pytest": get_ver("pytest"),
                "ruff": get_ver("ruff"),
                "black": get_ver("black"),
            },
            f,
            indent=2,
        )
    with open(WORK_DIR / "check_output.txt", "w") as f:
        f.write("\n".join(log_lines) + "\n")

    log("=" * 60)
    log("All R24-T018 checks passed. Evidence in work/R24-T018/")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
