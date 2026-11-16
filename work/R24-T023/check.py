"""Focused check for R24-T023: cross-check find_min_rotate.

Run from the repository root:

    python3 work/R24-T023/check.py

It exits non-zero if any of these fails:

1. The focused regression tests (``TestFindMinRotateCrossCheck`` in
   ``tests/test_searching.py``), run with pytest using the project's pytest
   settings from ``pyproject.toml``. A run that collects zero tests counts as
   a failure.
2. The three source anchors and two neighbouring inputs, each with a
   hand-calculated expected value.
3. A cross-check of ``find_min_rotate`` against an independent oracle (a plain
   linear scan, no binary search) on every rotation of sorted, duplicate-free
   lists of length 1-7 (28 inputs). The expected value is also known by
   construction: the first value of the sorted list. Each input is run twice
   on fresh copies; both results must equal the expected value and neither
   input may be modified.

It also records, without asserting, how ``find_min_rotate_recur`` does on the
same 28 inputs. It has a known defect, written up in findings.md. As agreed
for this task, that defect is documented here and not fixed.

The functions do no I/O, so there is nothing external to mock.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, findings.md and check_output.txt.
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test.
from algorithms.searching.find_min_rotate import (  # noqa: E402
    find_min_rotate,
    find_min_rotate_recur,
)

TEST_NODE = "tests/test_searching.py::TestFindMinRotateCrossCheck"
SORTED_VALUES = [-5, -2, 0, 3, 4, 9, 12]
FUNCTIONS = {
    "find_min_rotate": find_min_rotate,
    "find_min_rotate_recur": find_min_rotate_recur,
}

# Expected values calculated by hand before running the source.
ANCHORS = [
    {
        "name": "anchor_rotated",
        "function": "find_min_rotate",
        "args": [[4, 5, 6, 7, 0, 1, 2]],
        "expected": 0,
    },
    {
        "name": "anchor_not_rotated",
        "function": "find_min_rotate",
        "args": [[1, 2, 3]],
        "expected": 1,
    },
    {
        "name": "anchor_recursive",
        "function": "find_min_rotate_recur",
        "args": [[4, 5, 6, 7, 0, 1, 2], 0, 6],
        "expected": 0,
    },
    {
        "name": "neighbour_first_anchor_one_more_left_rotation",
        "function": "find_min_rotate",
        "args": [[5, 6, 7, 0, 1, 2, 4]],
        "expected": 0,
    },
    {
        "name": "neighbour_second_anchor_one_right_rotation",
        "function": "find_min_rotate",
        "args": [[3, 1, 2]],
        "expected": 1,
    },
]


def reference_min(array: list[int]) -> int:
    """Independent oracle: a plain linear scan (no binary search)."""
    smallest = array[0]
    for value in array[1:]:
        if value < smallest:
            smallest = value
    return smallest


def rotated_inputs() -> list[dict]:
    cases = []
    for n in range(1, len(SORTED_VALUES) + 1):
        base = SORTED_VALUES[-n:]
        for k in range(n):
            cases.append(
                {"input": base[k:] + base[:k], "left_rotation": k, "expected": base[0]}
            )
    return cases


def call(function, *args) -> object:
    """Call a function under test; report an exception instead of crashing."""
    try:
        return function(*args)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"


def fresh(args: list) -> list:
    return [list(a) if isinstance(a, list) else a for a in args]


def run_anchors() -> list[dict]:
    results = []
    for case in ANCHORS:
        args = fresh(case["args"])
        actual = call(FUNCTIONS[case["function"]], *args)
        unchanged = args == case["args"]
        results.append(
            {
                **case,
                "actual": actual,
                "input_unchanged": unchanged,
                "passed": actual == case["expected"] and unchanged,
            }
        )
    return results


def run_cross_check() -> list[dict]:
    results = []
    for case in rotated_inputs():
        array = case["input"]
        oracle = reference_min(array)
        first_input, second_input = list(array), list(array)
        first = call(find_min_rotate, first_input)
        second = call(find_min_rotate, second_input)
        unchanged = first_input == array and second_input == array
        results.append(
            {
                **case,
                "oracle": oracle,
                "actual_first_run": first,
                "actual_second_run": second,
                "input_unchanged": unchanged,
                "passed": oracle == case["expected"]
                and first == case["expected"]
                and second == first
                and unchanged,
            }
        )
    return results


def run_recursive_findings() -> dict:
    cases = rotated_inputs()
    mismatches = []
    for case in cases:
        array = case["input"]
        actual = call(find_min_rotate_recur, list(array), 0, len(array) - 1)
        if actual != case["expected"]:
            mismatches.append(
                {"input": array, "expected": case["expected"], "actual": actual}
            )
    smallest = min(mismatches, key=lambda m: len(m["input"])) if mismatches else None
    return {
        "asserted": False,
        "checked": len(cases),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "smallest_mismatch_found": smallest,
        "minimal_repro": {
            "call": "find_min_rotate_recur([2, 1], 0, 1)",
            "expected": 1,
            "actual": call(find_min_rotate_recur, [2, 1], 0, 1),
        },
    }


def run_pytest() -> dict:
    command = [sys.executable, "-m", "pytest", TEST_NODE, "-q", "--no-header"]
    proc = subprocess.run(
        command, cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    output = proc.stdout + proc.stderr
    passed = re.search(r"(\d+) passed", output)
    failed = re.search(r"(\d+) failed", output)
    n_passed = int(passed.group(1)) if passed else 0
    n_failed = int(failed.group(1)) if failed else 0
    return {
        "command": "python3 -m pytest " + TEST_NODE + " -q --no-header",
        "returncode": proc.returncode,
        "passed": n_passed,
        "failed": n_failed,
        "ok": proc.returncode == 0 and n_passed > 0 and n_failed == 0,
        "output": output,
    }


def tool_versions() -> dict:
    def version(pkg: str) -> str:
        try:
            return importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            return "not installed"

    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pytest": version("pytest"),
    }


def findings_markdown(cross: list[dict], recursive: dict) -> str:
    passed = sum(r["passed"] for r in cross)
    repro = recursive["minimal_repro"]
    smallest = recursive["smallest_mismatch_found"]
    lines = [
        "# R24-T023 findings",
        "",
        "## find_min_rotate (task target)",
        "",
        f"Matches the independent oracle on {passed} of {len(cross)} inputs "
        "(every rotation of sorted, duplicate-free lists of length 1-7). "
        "Repeated runs on fresh copies agree and no input is modified. "
        "No mismatch was found, so its code is unchanged.",
        "",
        "## find_min_rotate_recur (sibling function, used as an anchor only)",
        "",
        "Known defect: documented here, not fixed in this task (agreed scope).",
        "",
        "- The anchor `find_min_rotate_recur([4, 5, 6, 7, 0, 1, 2], 0, 6)` "
        "returns 0 as documented.",
        f"- On the same {recursive['checked']} inputs it returns the wrong "
        f"value for {recursive['mismatch_count']}.",
    ]
    if smallest:
        lines.append(
            f"- Smallest failing input found: `{smallest['input']}` returns "
            f"{smallest['actual']}, expected {smallest['expected']}."
        )
    lines += [
        f"- Minimal reproducible case: `{repro['call']}` returns "
        f"{repro['actual']}; expected {repro['expected']}.",
        "- Cause: the base case `if mid == low: return array[low]` (L59-60 at "
        "bd1d152) stops as soon as the range holds two items, without comparing "
        "`array[low]` with `array[high]`. When the minimum is at `high`, it is "
        "missed.",
        "- A minimal fix would stop when `low == high` instead. Not applied here.",
    ]
    return "\n".join(lines) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    anchors = run_anchors()
    cross = run_cross_check()
    recursive = run_recursive_findings()
    pytest_result = run_pytest()

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = ["R24-T023 find_min_rotate cross-check", ""]
    lines.append("Anchors and neighbouring inputs (expected vs actual):")
    for r in anchors:
        lines.append(
            f"  [{mark(r['passed'])}] {r['name']}: "
            f"{r['function']}({', '.join(repr(a) for a in r['args'])}) "
            f"expected={r['expected']} actual={r['actual']}"
        )
    lines.append("")
    lines.append(
        f"Cross-check vs linear-scan oracle: {sum(r['passed'] for r in cross)}"
        f"/{len(cross)} inputs passed"
    )
    for r in cross:
        lines.append(
            f"  [{mark(r['passed'])}] {r['input']}: expected={r['expected']} "
            f"oracle={r['oracle']} run1={r['actual_first_run']} "
            f"run2={r['actual_second_run']} unchanged={r['input_unchanged']}"
        )
    lines.append("")
    repro = recursive["minimal_repro"]
    lines.append(
        f"Recorded, not asserted: find_min_rotate_recur wrong on "
        f"{recursive['mismatch_count']}/{recursive['checked']} inputs; minimal "
        f"repro {repro['call']} -> {repro['actual']} (expected {repro['expected']})."
    )
    lines.append("")
    lines.append(f"Pytest command: {pytest_result['command']}")
    lines.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    lines.append(pytest_result["output"].rstrip())

    overall = (
        all(r["passed"] for r in anchors)
        and all(r["passed"] for r in cross)
        and len(cross) >= 20
        and pytest_result["ok"]
    )
    lines.append("")
    lines.append("OVERALL: " + mark(overall))
    report = "\n".join(lines) + "\n"

    write_json(
        "inputs.json",
        {
            "anchors_and_neighbours": ANCHORS,
            "cross_check_inputs": rotated_inputs(),
            "oracle": "linear scan (reference_min), plus expected-by-construction",
        },
    )
    write_json(
        "results.json",
        {
            "anchors_and_neighbours": anchors,
            "cross_check": cross,
            "find_min_rotate_recur_findings": recursive,
        },
    )
    write_json(
        "summary.json",
        {
            "task": "R24-T023",
            "target": "algorithms/searching/find_min_rotate.py:find_min_rotate",
            "anchors_passed": sum(r["passed"] for r in anchors),
            "anchors_total": len(anchors),
            "cross_check_passed": sum(r["passed"] for r in cross),
            "cross_check_total": len(cross),
            "recursive_mismatches_recorded": recursive["mismatch_count"],
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "findings.md").write_text(
        findings_markdown(cross, recursive), encoding="utf-8"
    )
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
