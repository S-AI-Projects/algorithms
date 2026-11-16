"""Focused check for R24-T027: a runnable worked example for geometric_mean.

Run from the repository root:

    python3 work/R24-T027/check.py

It exits non-zero if any of these fails:

1. The three source anchors and the neighbouring input [2, 8, 4], each
   against a hand-calculated expected value.
2. Hand-calculated intermediate states for [2, 8, 4] (product 1.0 -> 2.0 ->
   16.0 -> 64.0, n = 3, result 4.0 after rounding to 4 places), compared with
   one traced execution of the real function. ``sys.settrace`` records the
   ``product`` and ``n`` locals as the function runs; the source is not
   changed.
3. The docstring examples of ``geometric_mean`` are executed with doctest,
   and every displayed output must match (11 examples, 0 failures).
4. The focused regression tests (``TestGeometricMeanWorkedExample`` in
   ``tests/test_math.py``), run with pytest using the project's pytest
   settings from ``pyproject.toml``. A run that collects zero tests counts as
   a failure.

The function does no I/O, so there is nothing external to mock.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, worked_example.md and check_output.txt.
"""

from __future__ import annotations

import doctest
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
from algorithms.math.geometric_mean import geometric_mean  # noqa: E402

TEST_NODE = "tests/test_math.py::TestGeometricMeanWorkedExample"
NEIGHBOUR = [2, 8, 4]

# Expected values calculated by hand before running the source.
VALUE_CASES = [
    {"name": "anchor [1, 2, 3, 4, 5]", "input": [1, 2, 3, 4, 5], "expected": 2.6052},
    {"name": "anchor [2, 8]", "input": [2, 8], "expected": 4.0},
    {"name": "anchor [1, 1, 1]", "input": [1, 1, 1], "expected": 1.0},
    {"name": "neighbour [2, 8, 4]", "input": NEIGHBOUR, "expected": 4.0},
]
HAND_STATES = {
    "product_states": [1.0, 2.0, 16.0, 64.0],  # 1.0, then x2, x8, x4
    "n": 3,
    "result_rounded_to_4_places": 4.0,  # cube root of 64 is 4 (4 * 4 * 4 = 64)
}
EXPECTED_DOCTEST_EXAMPLES = 11  # 4 source anchors + 7 worked-example lines


def call_rounded(numbers: list[float]) -> object:
    try:
        return round(geometric_mean(list(numbers)), 4)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"


def run_value_cases() -> list[dict]:
    results = []
    for case in VALUE_CASES:
        argument = list(case["input"])
        actual = call_rounded(argument)
        results.append(
            {
                **case,
                "actual": actual,
                "input_unchanged": argument == case["input"],
                "passed": actual == case["expected"] and argument == case["input"],
            }
        )
    return results


def trace_execution(numbers: list[float]) -> dict:
    """Run geometric_mean once under sys.settrace and record its state."""
    products: list[float] = []
    n_values: list[int] = []
    code = geometric_mean.__code__

    def local_tracer(frame, event, arg):
        if event in ("line", "return"):
            local_vars = frame.f_locals
            product = local_vars.get("product")
            if product is not None and (not products or products[-1] != product):
                products.append(product)
            n = local_vars.get("n")
            if n is not None and not n_values:
                n_values.append(n)
        return local_tracer

    def global_tracer(frame, event, arg):
        if event == "call" and frame.f_code is code:
            return local_tracer
        return None

    previous = sys.gettrace()
    sys.settrace(global_tracer)
    try:
        result = geometric_mean(list(numbers))
    finally:
        sys.settrace(previous)
    return {
        "product_states": products,
        "n": n_values[0] if n_values else None,
        "raw_result": result,
        "result_rounded_to_4_places": round(result, 4),
    }


def run_doctests() -> dict:
    (test,) = doctest.DocTestFinder().find(
        geometric_mean, "geometric_mean", globs={"geometric_mean": geometric_mean}
    )
    examples = [
        {"source": ex.source.strip(), "displayed_output": ex.want.strip()}
        for ex in test.examples
    ]
    captured: list[str] = []
    results = doctest.DocTestRunner().run(test, out=captured.append)
    return {
        "examples": examples,
        "attempted": results.attempted,
        "failed": results.failed,
        "failure_report": "".join(captured),
        "passed": results.failed == 0
        and results.attempted == EXPECTED_DOCTEST_EXAMPLES,
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


def worked_example_markdown(trace: dict, state_rows: list[dict]) -> str:
    lines = [
        "# R24-T027 worked example for geometric_mean",
        "",
        "Input `[2, 8, 4]` (the anchor `[2, 8]` plus one value).",
        "",
        "| State | Hand-calculated | Traced execution | Result |",
        "|---|---|---|---|",
    ]
    for row in state_rows:
        lines.append(
            f"| {row['state']} | `{row['expected']}` | `{row['actual']}` "
            f"| {'PASS' if row['passed'] else 'FAIL'} |"
        )
    lines += [
        "",
        "Decisive transition: the loop only accumulates a product (64.0); "
        "the return line `product ** (1 / n)` turns it into the n-th root. "
        f"The raw traced result is `{trace['raw_result']!r}`. Floating-point "
        "roots can be off in the last digits, which is why the docstring "
        "examples round to 4 places.",
    ]
    return "\n".join(lines) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    values = run_value_cases()
    trace = trace_execution(NEIGHBOUR)
    state_rows = [
        {
            "state": key,
            "expected": expected,
            "actual": trace.get(key),
            "passed": trace.get(key) == expected,
        }
        for key, expected in HAND_STATES.items()
    ]
    doctests = run_doctests()
    pytest_result = run_pytest()

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = ["R24-T027 geometric_mean worked-example check", ""]
    lines.append("Anchors and neighbouring input (expected vs actual, rounded):")
    for r in values:
        lines.append(
            f"  [{mark(r['passed'])}] {r['name']}: expected={r['expected']} "
            f"actual={r['actual']}"
        )
    lines.append("")
    lines.append("Intermediate state for [2, 8, 4], hand vs traced execution:")
    for row in state_rows:
        lines.append(
            f"  [{mark(row['passed'])}] {row['state']}: expected={row['expected']} "
            f"actual={row['actual']}"
        )
    lines.append(f"  raw traced result: {trace['raw_result']!r}")
    lines.append("")
    lines.append(
        f"[{mark(doctests['passed'])}] docstring examples executed: "
        f"{doctests['attempted']} attempted (expected {EXPECTED_DOCTEST_EXAMPLES}), "
        f"{doctests['failed']} failed"
    )
    if doctests["failure_report"]:
        lines.append(doctests["failure_report"].rstrip())
    lines.append("")
    lines.append(f"Pytest command: {pytest_result['command']}")
    lines.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    lines.append(pytest_result["output"].rstrip())

    overall = (
        all(r["passed"] for r in values)
        and all(row["passed"] for row in state_rows)
        and doctests["passed"]
        and pytest_result["ok"]
    )
    lines.append("")
    lines.append("OVERALL: " + mark(overall))
    report = "\n".join(lines) + "\n"

    write_json(
        "inputs.json",
        {
            "value_cases": VALUE_CASES,
            "traced_input": NEIGHBOUR,
            "hand_calculated_states": HAND_STATES,
            "expected_doctest_examples": EXPECTED_DOCTEST_EXAMPLES,
        },
    )
    write_json(
        "results.json",
        {
            "value_cases": values,
            "traced_execution": trace,
            "state_comparison": state_rows,
            "doctests": doctests,
        },
    )
    write_json(
        "summary.json",
        {
            "task": "R24-T027",
            "target": "algorithms/math/geometric_mean.py:geometric_mean",
            "value_cases_passed": sum(r["passed"] for r in values),
            "value_cases_total": len(values),
            "states_match_trace": all(row["passed"] for row in state_rows),
            "doctest_examples_attempted": doctests["attempted"],
            "doctest_examples_failed": doctests["failed"],
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "worked_example.md").write_text(
        worked_example_markdown(trace, state_rows), encoding="utf-8"
    )
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
