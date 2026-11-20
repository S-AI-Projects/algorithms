#!/usr/bin/env python3
"""Focused check runner for R24-T042: supported boundaries of ListNode.

1. Checks each documented boundary of ListNode directly against an expected
   value worked out by hand from the docstring contract.
2. Runs the focused pytest class with the project's pytest configuration:
   tests/test_linked_list.py::TestListNodeBoundaries

Writes evidence (inputs, expected vs actual, tool versions, boundary table)
to work/R24-T042/ and exits non-zero if any check fails. ListNode has no
external I/O, so nothing needs mocking.

Usage:
    python3 work/R24-T042/check.py
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T042"
sys.path.insert(0, str(ROOT))

from algorithms.common.list_node import ListNode  # noqa: E402

SOURCE = "algorithms/common/list_node.py"
PYTEST_TARGET = "tests/test_linked_list.py::TestListNodeBoundaries"


def values(head):
    out = []
    while head is not None:
        out.append(head.val)
        head = head.next
    return out


def cycle_repr():
    node = ListNode(1)
    node.next = node
    return repr(node)


def hash_result():
    try:
        hash(ListNode())
    except TypeError:
        return "TypeError"
    return "hashable"


def neighbor():
    head = ListNode(1, ListNode(2, ListNode(3)))
    return values(ListNode(0, head)), values(head)


def shared_tail():
    tail = ListNode(2)
    head = ListNode(1, tail)
    tail.val = 9
    return values(head)


def relink():
    head = ListNode(1, ListNode(2, ListNode(3)))
    head.next = head.next.next
    return values(head)


# (boundary, side, expression, callable, expected, source citation)
CASES = [
    (
        "anchor",
        "interior",
        "ListNode(1, ListNode(2, ListNode(3))).val",
        lambda: ListNode(1, ListNode(2, ListNode(3))).val,
        1,
        "L49-L51",
    ),
    (
        "anchor",
        "interior",
        "ListNode(1, ListNode(2, ListNode(3))).next.val",
        lambda: ListNode(1, ListNode(2, ListNode(3))).next.val,
        2,
        "L49, L52-L53",
    ),
    (
        "neighbor",
        "interior",
        "values(ListNode(0, head)), values(head)",
        neighbor,
        ([0, 1, 2, 3], [1, 2, 3]),
        "L23-L26",
    ),
    (
        "construction",
        "boundary",
        "(ListNode().val, ListNode().next)",
        lambda: (ListNode().val, ListNode().next),
        (0, None),
        "L23-L24, L58-L59",
    ),
    (
        "end of list",
        "boundary",
        "ListNode(7).next",
        lambda: ListNode(7).next,
        None,
        "L27-L28",
    ),
    (
        "end of list",
        "interior",
        "values(ListNode(7, ListNode(8)))",
        lambda: values(ListNode(7, ListNode(8))),
        [7, 8],
        "L27-L28",
    ),
    (
        "truthiness",
        "boundary",
        "bool(ListNode(0))",
        lambda: bool(ListNode(0)),
        True,
        "L29-L30",
    ),
    (
        "equality",
        "equal",
        "ListNode(1, ListNode(2)) == ListNode(1, ListNode(2))",
        lambda: ListNode(1, ListNode(2)) == ListNode(1, ListNode(2)),
        True,
        "L31-L34",
    ),
    (
        "equality",
        "length differs",
        "ListNode(1) == ListNode(1, ListNode(2))",
        lambda: ListNode(1) == ListNode(1, ListNode(2)),
        False,
        "L31-L34",
    ),
    (
        "equality",
        "tail differs",
        "ListNode(1, ListNode(2)) == ListNode(1, ListNode(3))",
        lambda: ListNode(1, ListNode(2)) == ListNode(1, ListNode(3)),
        False,
        "L31-L34",
    ),
    (
        "equality",
        "non-node",
        "ListNode(1) == 1",
        lambda: ListNode(1) == 1,
        False,
        "L33-L34",
    ),
    (
        "construction",
        "no copy",
        "values after tail.val = 9",
        shared_tail,
        [1, 9],
        "L25-L26",
    ),
    (
        "mutation",
        "relink",
        "values after head.next = head.next.next",
        relink,
        [1, 3],
        "L35",
    ),
    (
        "repr",
        "boundary",
        "repr(ListNode())",
        lambda: repr(ListNode()),
        "ListNode(val=0, next=None)",
        "L39, L54-L55",
    ),
    (
        "repr",
        "cycle",
        "repr of node whose next is itself",
        cycle_repr,
        "ListNode(val=1, next=...)",
        "L39",
    ),
    ("hashing", "boundary", "hash(ListNode())", hash_result, "TypeError", "L36-L38"),
]

UNSUPPORTED = [
    ("val of a type other than int", "stored as given, not validated", "L42-L43, L58"),
    ("== or repr on very long lists", "may raise RecursionError", "L43-L46"),
    ("== between two different cyclic lists", "may raise RecursionError", "L45-L46"),
]


def tool_versions() -> dict[str, str]:
    versions = {"python": platform.python_version(), "platform": platform.platform()}
    try:
        versions["pytest"] = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        versions["pytest"] = "not installed"
    return versions


def as_json(value):
    return list(value) if isinstance(value, tuple) else value


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    failures = 0

    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    log("R24-T042: ListNode boundary checks")

    results = []
    for boundary, side, expr, func, expected, cite in CASES:
        actual = func()
        ok = actual == expected
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [{boundary} / {side}] {expr} "
            f"expected={expected!r} actual={actual!r}"
        )
        results.append(
            {
                "boundary": boundary,
                "side": side,
                "expression": expr,
                "expected": as_json(expected),
                "actual": as_json(actual),
                "source": f"{SOURCE} {cite}",
                "passed": ok,
            }
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
            [
                {
                    "boundary": c[0],
                    "side": c[1],
                    "expression": c[2],
                    "expected": as_json(c[4]),
                }
                for c in CASES
            ],
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "cases": results,
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

    table = [
        "# ListNode boundary table (R24-T042)",
        "",
        f"Source: `{SOURCE}` (docstring contract and dataclass fields).",
        "",
        "| Boundary | Side | Check | Expected | Actual | Source |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        table.append(
            f"| {r['boundary']} | {r['side']} | `{r['expression']}` | "
            f"`{r['expected']!r}` | `{r['actual']!r}` | {r['source']} |"
        )
    table += [
        "",
        "## Unsupported (documented, not tested, no new guards added)",
        "",
        "| Input | Behavior | Source |",
        "|---|---|---|",
    ]
    for what, behavior, cite in UNSUPPORTED:
        table.append(f"| {what} | {behavior} | {SOURCE} {cite} |")
    (WORK / "boundary_table.md").write_text("\n".join(table) + "\n")
    (WORK / "check_output.txt").write_text("\n".join(lines) + "\n")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
