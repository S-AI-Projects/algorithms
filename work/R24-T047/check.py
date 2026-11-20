#!/usr/bin/env python3
"""Focused check runner for R24-T047: executable worked example of pancake_sort.

1. Runs every example in the pancake_sort docstring with doctest and
   records each displayed output next to the actual output.
2. Traces the list state after every flip (with a list subclass that
   records slice assignments) and compares it with the states worked out
   by hand for [3, 1, 2], [1, 3, 2], [2, 2, 1], [1, 2, 3], [3, 2, 1], []
   and [5].
3. Checks the list is sorted in place and the same object is returned.
4. Runs the focused pytest class with the project's pytest configuration:
   tests/test_sorting.py::TestPancakeSortWorkedExample

Writes evidence (including worked_example.md) to work/R24-T047/ and exits
non-zero if any check fails. pancake_sort has no external I/O, so nothing
needs mocking.

Usage:
    python3 work/R24-T047/check.py
"""

from __future__ import annotations

import doctest
import importlib
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T047"
sys.path.insert(0, str(ROOT))

MODULE = importlib.import_module("algorithms.sorting.pancake_sort")
pancake_sort = MODULE.pancake_sort

PYTEST_TARGET = "tests/test_sorting.py::TestPancakeSortWorkedExample"

# input -> (state after each flip, worked out by hand; final result)
HAND_TRACES = [
    ([3, 1, 2], [[2, 1, 3], [1, 2, 3]], [1, 2, 3]),
    ([1, 3, 2], [[3, 1, 2], [2, 1, 3], [1, 2, 3]], [1, 2, 3]),
    ([2, 2, 1], [[1, 2, 2]], [1, 2, 2]),
    ([1, 2, 3], [], [1, 2, 3]),
    ([3, 2, 1], [[1, 2, 3]], [1, 2, 3]),
    ([], [], []),
    ([5], [], [5]),
]


class FlipRecorder(list):
    def __init__(self, values):
        super().__init__(values)
        self.states = []

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self.states.append(list(self))


def run_docstring_examples():
    """Run each docstring example in order; return (source, want, got) rows."""
    test = doctest.DocTestFinder().find(MODULE.pancake_sort, "pancake_sort")[0]
    namespace = dict(test.globs)
    rows = []
    for example in test.examples:
        source = example.source.strip()
        try:
            value = eval(source, namespace)  # noqa: S307 - our own docstring
            got = "" if value is None else repr(value) + "\n"
        except SyntaxError:
            exec(source, namespace)  # noqa: S102 - statement in our docstring
            got = ""
        rows.append((source, example.want, got))
    return rows


def tool_versions() -> dict[str, str]:
    versions = {"python": platform.python_version(), "platform": platform.platform()}
    try:
        versions["pytest"] = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        versions["pytest"] = "not installed"
    return versions


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    failures = 0

    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    log("R24-T047: pancake_sort worked example checks")

    doc_rows = []
    for source, want, got in run_docstring_examples():
        ok = want == got
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [docstring] >>> {source}  "
            f"displayed={want.strip()!r} actual={got.strip()!r}"
        )
        doc_rows.append(
            {"example": source, "displayed": want.strip(), "actual": got.strip()}
        )
    doctest_result = doctest.testmod(MODULE, verbose=False)
    ok = doctest_result.failed == 0 and doctest_result.attempted == 10
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [doctest] doctest.testmod: expected 10 "
        f"attempted / 0 failed, actual {doctest_result.attempted} attempted / "
        f"{doctest_result.failed} failed"
    )

    trace_rows = []
    for values, expected_states, expected_result in HAND_TRACES:
        recorder = FlipRecorder(values)
        result = pancake_sort(recorder)
        ok = recorder.states == expected_states and list(result) == expected_result
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [trace] {values}: expected flips "
            f"{expected_states} -> {expected_result}, actual {recorder.states} "
            f"-> {list(result)}"
        )
        trace_rows.append(
            {
                "input": values,
                "expected_states": expected_states,
                "actual_states": recorder.states,
                "expected_result": expected_result,
                "actual_result": list(result),
                "passed": ok,
            }
        )

    data = [2, 2, 1]
    ok = pancake_sort(data) is data and data == [1, 2, 2]
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [in place] pancake_sort(data) is data, "
        f"expected data=[1, 2, 2], actual data={data}"
    )

    cmd = [sys.executable, "-m", "pytest", PYTEST_TARGET]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    match = re.search(r"(\d+) passed", proc.stdout)
    passed = int(match.group(1)) if match else 0
    ok = proc.returncode == 0 and passed > 0
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [pytest] python3 -m pytest {PYTEST_TARGET} "
        f"-> exit={proc.returncode}, {passed} passed"
    )
    if not ok:
        log(proc.stdout[-2000:] + proc.stderr[-2000:])

    log(f"RESULT: {'OK' if failures == 0 else f'{failures} FAILED'}")

    (WORK / "inputs.json").write_text(
        json.dumps(
            {
                "hand_traces": [
                    {"input": v, "states_after_each_flip": s, "result": r}
                    for v, s, r in HAND_TRACES
                ],
                "docstring_examples": [row["example"] for row in doc_rows],
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "docstring_examples": doc_rows,
                "doctest": {
                    "attempted": doctest_result.attempted,
                    "failed": doctest_result.failed,
                },
                "traces": trace_rows,
                "pytest": {
                    "command": f"python3 -m pytest {PYTEST_TARGET}",
                    "exit_code": proc.returncode,
                    "passed": passed,
                },
                "failures": failures,
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "tool_versions.json").write_text(
        json.dumps(tool_versions(), indent=2) + "\n"
    )

    md = [
        "# pancake_sort worked example (R24-T047)",
        "",
        "A flip reverses a prefix. Each pass handles the unsorted prefix",
        "`array[:cur]`. Decisive transition: after the pass for `cur`, the",
        "prefix's largest value is at index `cur - 1` and is never moved again.",
        "",
        "| Input | State after each flip (hand = traced) | Result |",
        "|---|---|---|",
    ]
    for row in trace_rows:
        states = " → ".join(str(s) for s in row["actual_states"]) or "no flips"
        md.append(f"| `{row['input']}` | {states} | `{row['actual_result']}` |")
    (WORK / "worked_example.md").write_text("\n".join(md) + "\n")
    (WORK / "check_output.txt").write_text("\n".join(lines) + "\n")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
