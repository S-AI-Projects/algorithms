"""Focused check for R24-T022: supported boundaries of first_switch_pairs.

Run from the repository root:

    python3 work/R24-T022/check.py

It does three things and exits non-zero if any of them fails:

1. Runs the focused regression tests (``TestFirstSwitchPairsBoundaries`` in
   ``tests/test_stack.py``) with pytest, using the project's pytest settings
   from ``pyproject.toml``. A run that collects zero tests counts as a failure.
2. Walks the issue fixture on a plain list used as a stack (push A, B, C;
   pop twice; push D; drain), checks the pop order C, B, D, A, and calls
   ``first_switch_pairs`` on a copy of the stack at every state.
3. Calls ``first_switch_pairs`` directly on each boundary input and checks
   the value and that the same list object is rearranged in place.

The function does no I/O, so there is nothing external to mock.

Source lines are cited at the pinned commit bd1d152 of
algorithms/stack/switch_pairs.py:
  L4      "Switch successive pairs of values in a stack starting from the bottom."
  L5      "If there is an odd number of values, the top element is not moved."
  L24     "stack: A list representing a stack (bottom to top)."
  L33-44  implementation (loops at L34 and L36, odd case at L38-40,
          swap at L41-43, ``return stack`` at L44).

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, boundary_table.md and check_output.txt.
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
from algorithms.stack.switch_pairs import first_switch_pairs  # noqa: E402

TEST_NODE = "tests/test_stack.py::TestFirstSwitchPairsBoundaries"

# Expected values derived by hand from the source contract (L4-5, L24).
CASES = [
    {
        "partition": "valid boundary",
        "name": "empty_stack",
        "input": [],
        "expected": [],
        "source": "L34/L36 loops run zero times; L44 returns stack",
    },
    {
        "partition": "valid boundary",
        "name": "single_value",
        "input": [7],
        "expected": [7],
        "source": "L5; odd case L38-40",
    },
    {
        "partition": "valid boundary",
        "name": "smallest_even",
        "input": [1, 2],
        "expected": [2, 1],
        "source": "L4; swap L41-43",
    },
    {
        "partition": "valid boundary",
        "name": "smallest_odd_with_pair",
        "input": [1, 2, 3],
        "expected": [2, 1, 3],
        "source": "L5; odd case L38-40",
    },
    {
        "partition": "valid interior",
        "name": "even_four",
        "input": [1, 2, 3, 4],
        "expected": [2, 1, 4, 3],
        "source": "L4",
    },
    {
        "partition": "valid interior",
        "name": "docstring_example",
        "input": [3, 8, 17, 9, 1, 10],
        "expected": [8, 3, 9, 17, 10, 1],
        "source": "L30-31 (existing doctest)",
    },
]

FIXTURE = {
    "operations": "push A, B, C; pop twice; push D; drain",
    "expected_pop_order": ["C", "B", "D", "A"],
    "states": [
        {
            "after": "push A, B, C",
            "stack": ["A", "B", "C"],
            "switched": ["B", "A", "C"],
        },
        {"after": "pop twice", "stack": ["A"], "switched": ["A"]},
        {"after": "push D", "stack": ["A", "D"], "switched": ["D", "A"]},
        {"after": "drain", "stack": [], "switched": []},
    ],
}

UNSUPPORTED = {
    "partition": "unsupported",
    "name": "non_list_argument",
    "input": "a tuple or None",
    "note": "No guard in the source (L33-44) and no documented exception, "
    "so behaviour is undefined and no exception is asserted.",
}


def call_switch(argument: list) -> object:
    """Call the function under test; report an exception instead of crashing."""
    try:
        return first_switch_pairs(argument)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"


def run_direct_cases() -> list[dict]:
    results = []
    for case in CASES:
        argument = list(case["input"])
        actual = call_switch(argument)
        value_ok = actual == case["expected"]
        in_place = actual is argument
        results.append(
            {
                **case,
                "actual": actual,
                "value_ok": value_ok,
                "same_list_returned": in_place,
                "passed": value_ok and in_place,
            }
        )
    return results


def run_fixture() -> dict:
    stack: list[str] = []
    popped: list[str] = []
    states = []

    def record(after: str) -> None:
        expected = next(s for s in FIXTURE["states"] if s["after"] == after)
        switched = call_switch(list(stack))
        states.append(
            {
                "after": after,
                "expected_stack": expected["stack"],
                "actual_stack": list(stack),
                "expected_switched": expected["switched"],
                "actual_switched": switched,
                "passed": stack == expected["stack"]
                and switched == expected["switched"],
            }
        )

    for value in ("A", "B", "C"):
        stack.append(value)
    record("push A, B, C")
    popped.append(stack.pop())
    popped.append(stack.pop())
    record("pop twice")
    stack.append("D")
    record("push D")
    while stack:
        popped.append(stack.pop())
    record("drain")

    pop_order_ok = popped == FIXTURE["expected_pop_order"]
    return {
        "operations": FIXTURE["operations"],
        "expected_pop_order": FIXTURE["expected_pop_order"],
        "actual_pop_order": popped,
        "pop_order_ok": pop_order_ok,
        "states": states,
        "passed": pop_order_ok and all(s["passed"] for s in states),
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


def boundary_table(direct: list[dict], fixture: dict) -> str:
    rows = [
        "# R24-T022 boundary table for first_switch_pairs",
        "",
        "Source: algorithms/stack/switch_pairs.py at bd1d152. The stack is read",
        "bottom to top (L24): index 0 is the bottom, the last item is the top.",
        "",
        "| Partition | Input | Expected | Actual | Same list | Source | Result |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in direct:
        rows.append(
            f"| {r['partition']} | `{r['input']}` | `{r['expected']}` "
            f"| `{r['actual']}` | {r['same_list_returned']} | {r['source']} "
            f"| {'PASS' if r['passed'] else 'FAIL'} |"
        )
    rows.append(
        f"| {UNSUPPORTED['partition']} | {UNSUPPORTED['input']} | undefined "
        f"| not executed | n/a | L33-44, no guard | n/a |"
    )
    rows += [
        "",
        f"Fixture: {fixture['operations']}. Expected pop order "
        f"{fixture['expected_pop_order']}, actual {fixture['actual_pop_order']}.",
        "",
        "| After | Stack | first_switch_pairs(copy) expected | Actual | Result |",
        "|---|---|---|---|---|",
    ]
    for s in fixture["states"]:
        rows.append(
            f"| {s['after']} | `{s['actual_stack']}` | `{s['expected_switched']}` "
            f"| `{s['actual_switched']}` | {'PASS' if s['passed'] else 'FAIL'} |"
        )
    rows += ["", f"Unsupported note: {UNSUPPORTED['note']}"]
    return "\n".join(rows) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    direct = run_direct_cases()
    fixture = run_fixture()
    pytest_result = run_pytest()

    lines = ["R24-T022 first_switch_pairs boundary check", ""]
    lines.append(f"Fixture: {fixture['operations']}")
    lines.append(
        f"  [{'PASS' if fixture['pop_order_ok'] else 'FAIL'}] pop order: "
        f"expected={fixture['expected_pop_order']} "
        f"actual={fixture['actual_pop_order']}"
    )
    for s in fixture["states"]:
        lines.append(
            f"  [{'PASS' if s['passed'] else 'FAIL'}] after {s['after']}: "
            f"stack={s['actual_stack']} "
            f"switched expected={s['expected_switched']} "
            f"actual={s['actual_switched']}"
        )
    lines.append("")
    lines.append("Boundary cases (expected vs actual):")
    for r in direct:
        lines.append(
            f"  [{'PASS' if r['passed'] else 'FAIL'}] {r['partition']} "
            f"{r['name']}: input={r['input']} expected={r['expected']} "
            f"actual={r['actual']} same_list_returned={r['same_list_returned']}"
        )
    lines.append(
        f"  [SKIP] {UNSUPPORTED['partition']} {UNSUPPORTED['name']}: "
        f"{UNSUPPORTED['note']}"
    )
    lines.append("")
    lines.append(f"Pytest command: {pytest_result['command']}")
    lines.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    lines.append(pytest_result["output"].rstrip())

    overall = (
        fixture["passed"] and all(r["passed"] for r in direct) and pytest_result["ok"]
    )
    lines.append("")
    lines.append("OVERALL: " + ("PASS" if overall else "FAIL"))
    report = "\n".join(lines) + "\n"

    write_json(
        "inputs.json",
        {"boundary_cases": CASES, "fixture": FIXTURE, "unsupported": UNSUPPORTED},
    )
    write_json("results.json", {"fixture": fixture, "boundary_cases": direct})
    write_json(
        "summary.json",
        {
            "task": "R24-T022",
            "target": "algorithms/stack/switch_pairs.py:first_switch_pairs",
            "fixture_passed": fixture["passed"],
            "boundary_cases": len(direct),
            "boundary_cases_passed": sum(r["passed"] for r in direct),
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": "PASS" if overall else "FAIL",
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "boundary_table.md").write_text(
        boundary_table(direct, fixture), encoding="utf-8"
    )
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
