"""Focused check for R24-T028: the empty-result path of matrix_chain_order.

Run from the repository root:

    python3 work/R24-T028/check.py

``matrix_chain_order`` has no error branch: it validates nothing and raises
nothing. So, as the issue says for a total contract, this covers its valid
empty result instead of inventing an exception. With at most one matrix
(``len(array) <= 2``) the loop over chain lengths does not run (L39 at commit
bd1d152), and the tables keep the zeros they start with (L37-38). The result
is returned at L51: cost 0 and split 0, meaning "no split".

It exits non-zero if any of these fails:

1. The fixture inputs (one 2 x 3 rectangular matrix, one 1 x 1 matrix, one
   0 x 3 zero-dimension matrix) and the smallest inputs ([] and [5]) return
   the expected empty result. A line trace proves each one reaches the
   branch: the L39 loop header runs, the loop body (L40-50) does not, and
   the function returns.
2. Caller-owned state stays valid. The input list is unchanged, and the
   returned tables belong to the caller: editing them does not affect a
   later call.
3. Ordinary calls succeed afterwards: [2, 3, 4] costs 24 with split 1, and
   the docstring chain costs 15125 with split 3. Their loop body does run,
   and no _INF placeholder (L43) is left in their tables.
4. The focused regression tests (``TestMatrixChainOrderEmptyResult`` in
   ``tests/test_dynamic_programming.py``), run with pytest using the
   project's pytest settings from ``pyproject.toml``. A run that collects
   zero tests counts as a failure.

The function does no I/O, so there is nothing external to mock.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, branch.md and check_output.txt.
"""

from __future__ import annotations

import importlib.metadata
import inspect
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
from algorithms.dynamic_programming.matrix_chain_order import (  # noqa: E402
    matrix_chain_order,
)

TEST_NODE = "tests/test_dynamic_programming.py::TestMatrixChainOrderEmptyResult"

# Statements named by their line at the pinned commit bd1d152.
STATEMENTS = {
    "loop_header": ("for chain_length in range(2, n):", "L39"),
    "loop_body": ("for a in range(1, n - chain_length + 1):", "L40"),
    "return": ("return matrix, sol", "L51"),
}

ZERO_2X2 = [[0, 0], [0, 0]]
# Expected values calculated by hand before running the source.
EMPTY_CASES = [
    {"name": "2 x 3 rectangular matrix", "input": [2, 3], "expected": [ZERO_2X2] * 2},
    {"name": "1 x 1 matrix", "input": [1, 1], "expected": [ZERO_2X2] * 2},
    {
        "name": "0 x 3 zero-dimension matrix",
        "input": [0, 3],
        "expected": [ZERO_2X2] * 2,
    },
    {"name": "smallest input []", "input": [], "expected": [[], []]},
    {"name": "one dimension [5]", "input": [5], "expected": [[[0]], [[0]]]},
]
ORDINARY_CASES = [
    {
        "name": "2 x 3 times 3 x 4",
        "input": [2, 3, 4],
        "cell": [1, 2],
        "expected": {"cost": 24, "split": 1},
    },
    {
        "name": "docstring chain",
        "input": [30, 35, 15, 5, 10, 20, 25],
        "cell": [1, 6],
        "expected": {"cost": 15125, "split": 3},
    },
]


def current_lines() -> dict[str, int]:
    """Find where each named statement is in the current source file."""
    source_lines, start = inspect.getsourcelines(matrix_chain_order)
    found = {}
    for key, (text, _) in STATEMENTS.items():
        for offset, line in enumerate(source_lines):
            if line.strip() == text:
                found[key] = start + offset
                break
    return found


def traced_call(dims: list[int]) -> tuple[object, set[int]]:
    """Call matrix_chain_order and record which of its lines ran."""
    executed: set[int] = set()
    code = matrix_chain_order.__code__

    def local_tracer(frame, event, arg):
        if event == "line":
            executed.add(frame.f_lineno)
        return local_tracer

    def global_tracer(frame, event, arg):
        if event == "call" and frame.f_code is code:
            return local_tracer
        return None

    previous = sys.gettrace()
    sys.settrace(global_tracer)
    try:
        result = matrix_chain_order(dims)
    except Exception as exc:
        result = f"raised {type(exc).__name__}: {exc}"
    finally:
        sys.settrace(previous)
    return result, executed


def reach(executed: set[int], lines: dict[str, int]) -> dict[str, bool]:
    return {key: lines.get(key) in executed for key in STATEMENTS}


def run_empty_cases(lines: dict[str, int]) -> list[dict]:
    results = []
    for case in EMPTY_CASES:
        dims = list(case["input"])
        result, executed = traced_call(dims)
        actual = list(result) if isinstance(result, tuple) else result
        reached = reach(executed, lines)
        branch_ok = reached == {"loop_header": True, "loop_body": False, "return": True}
        results.append(
            {
                **case,
                "actual": actual,
                "reached": reached,
                "input_unchanged": dims == case["input"],
                "passed": actual == case["expected"]
                and branch_ok
                and dims == case["input"],
            }
        )
    return results


def run_caller_state() -> dict:
    dims = [2, 3]
    expected = ([[0, 0], [0, 0]], [[0, 0], [0, 0]])
    try:
        first = matrix_chain_order(dims)
        first[0][1][1] = 99  # the caller edits the returned cost table
        again = matrix_chain_order([2, 3])
        later_call: object = [list(t) for t in again]
    except Exception as exc:
        again = None
        later_call = f"raised {type(exc).__name__}: {exc}"
    return {
        "name": "returned tables belong to the caller; input unchanged",
        "expected": {"later_call": [list(t) for t in expected], "dims": [2, 3]},
        "actual": {"later_call": later_call, "dims": dims},
        "passed": again == expected and dims == [2, 3],
    }


def run_ordinary_cases(lines: dict[str, int]) -> list[dict]:
    results = []
    for case in ORDINARY_CASES:
        dims = list(case["input"])
        result, executed = traced_call(dims)
        if isinstance(result, tuple):
            m, s = result
            i, j = case["cell"]
            actual = {"cost": m[i][j], "split": s[i][j]}
            inf_left = any(v == float("inf") for row in m for v in row)
        else:
            actual, inf_left = result, None
        reached = reach(executed, lines)
        results.append(
            {
                **case,
                "actual": actual,
                "reached": reached,
                "inf_left_in_table": inf_left,
                "passed": actual == case["expected"]
                and reached["loop_body"]
                and inf_left is False
                and dims == case["input"],
            }
        )
    return results


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


def branch_markdown(lines: dict[str, int], empty: list[dict]) -> str:
    rows = [
        "# R24-T028 branch covered in matrix_chain_order",
        "",
        "There is no error branch, so the covered path is the valid empty "
        "result: with at most one matrix (`len(array) <= 2`) the loop over "
        "chain lengths does not run, and the zero tables from L37-38 are "
        "returned at L51.",
        "",
        "| Statement | Line at bd1d152 | Line on this branch |",
        "|---|---|---|",
    ]
    for key, (text, pinned) in STATEMENTS.items():
        rows.append(f"| `{text}` | {pinned} | L{lines.get(key)} |")
    rows += [
        "",
        "| Input | Loop header ran | Loop body ran | Returned | Result |",
        "|---|---|---|---|---|",
    ]
    for r in empty:
        rows.append(
            f"| `{r['input']}` ({r['name']}) | {r['reached']['loop_header']} "
            f"| {r['reached']['loop_body']} | {r['reached']['return']} "
            f"| {'PASS' if r['passed'] else 'FAIL'} |"
        )
    return "\n".join(rows) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    lines = current_lines()
    empty = run_empty_cases(lines)
    caller = run_caller_state()
    ordinary = run_ordinary_cases(lines)
    pytest_result = run_pytest()

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    out = ["R24-T028 matrix_chain_order empty-result check", ""]
    out.append(
        "Named statements (pinned bd1d152 -> this branch): "
        + ", ".join(
            f"{pinned} -> L{lines.get(key)} {text!r}"
            for key, (text, pinned) in STATEMENTS.items()
        )
    )
    out.append("")
    out.append("Empty-result cases (expected vs actual, and lines reached):")
    for r in empty:
        out.append(
            f"  [{mark(r['passed'])}] {r['name']} {r['input']}: "
            f"expected={r['expected']} actual={r['actual']} reached={r['reached']}"
        )
    out.append("")
    out.append(
        f"[{mark(caller['passed'])}] {caller['name']}: expected={caller['expected']} "
        f"actual={caller['actual']}"
    )
    out.append("")
    out.append("Ordinary calls afterwards:")
    for r in ordinary:
        out.append(
            f"  [{mark(r['passed'])}] {r['name']} {r['input']} cell {r['cell']}: "
            f"expected={r['expected']} actual={r['actual']} "
            f"loop body ran={r['reached']['loop_body']} "
            f"_INF left={r['inf_left_in_table']}"
        )
    out.append("")
    out.append(f"Pytest command: {pytest_result['command']}")
    out.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    out.append(pytest_result["output"].rstrip())

    overall = (
        len(lines) == len(STATEMENTS)
        and all(r["passed"] for r in empty)
        and caller["passed"]
        and all(r["passed"] for r in ordinary)
        and pytest_result["ok"]
    )
    out.append("")
    out.append("OVERALL: " + mark(overall))
    report = "\n".join(out) + "\n"

    write_json(
        "inputs.json",
        {
            "named_statements": {k: v[1] for k, v in STATEMENTS.items()},
            "empty_result_cases": EMPTY_CASES,
            "ordinary_cases": ORDINARY_CASES,
        },
    )
    write_json(
        "results.json",
        {
            "current_lines": lines,
            "empty_result_cases": empty,
            "caller_state": caller,
            "ordinary_cases": ordinary,
        },
    )
    write_json(
        "summary.json",
        {
            "task": "R24-T028",
            "target": "algorithms/dynamic_programming/matrix_chain_order.py:"
            "matrix_chain_order",
            "branch": "L39 loop skipped when len(array) <= 2; zero tables "
            "(L37-38) returned at L51",
            "empty_cases_passed": sum(r["passed"] for r in empty),
            "empty_cases_total": len(empty),
            "caller_state_passed": caller["passed"],
            "ordinary_cases_passed": sum(r["passed"] for r in ordinary),
            "ordinary_cases_total": len(ordinary),
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "branch.md").write_text(branch_markdown(lines, empty), encoding="utf-8")
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
