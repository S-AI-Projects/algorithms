"""Focused check for R24-T024: an invariant of Node in add_two_numbers.py.

Run from the repository root:

    python3 work/R24-T024/check.py

Invariant (documented in the Node docstring):
  - ``Node(x)`` stores ``x`` in ``val`` and starts with ``next`` set to None,
    so one node is the smallest supported list.
  - Following ``next`` from the head of a list of distinct linked nodes visits
    each node exactly once and stops at None.
  - Ownership: the module's functions only read the nodes they are given
    (``val`` and ``next`` stay the same) and return lists built from new nodes.

It exits non-zero if any of these fails:

1. The focused tests (``TestAddTwoNumbersNodeInvariant`` in
   ``tests/test_linked_list.py``), run with pytest using the project's pytest
   settings from ``pyproject.toml``. A run that collects zero tests counts as
   a failure.
2. The fixtures: three distinct nodes A->B->C, with values and links checked
   separately; the smallest supported list (one node); and the sum 342 + 5.
3. The property cases: 3 readable small cases plus 200 cases from
   ``random.Random(24024)``. Each case is a pair of non-negative integers with
   1-12 digits, the module's documented domain.

Every traversal is bounded, so a cycle is reported as a failure instead of
hanging. Module functions are not called on a list whose traversal failed. If
a property case fails, the smallest failing example is reported.

The module does no I/O, so there is nothing external to mock.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, invariant.md and check_output.txt.
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import random
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test.
from algorithms.linked_list.add_two_numbers import (  # noqa: E402
    Node,
    add_two_numbers,
    convert_to_str,
)

TEST_NODE = "tests/test_linked_list.py::TestAddTwoNumbersNodeInvariant"
SEED = 24024
RANDOM_CASES = 200
READABLE_CASES = [(0, 0), (5, 7), (342, 465)]


def build(digits: list[int]) -> tuple[Node, list[Node]]:
    """Link one new Node per digit and return (head, nodes)."""
    nodes = [Node(digit) for digit in digits]
    # The last node has no successor, so the lengths differ by one.
    for node, successor in zip(nodes, nodes[1:], strict=False):
        node.next = successor
    return nodes[0], nodes


def walk(head: Node | None, limit: int) -> tuple[list[Node], bool]:
    """Follow next from head. Return (visited, stopped_at_none)."""
    visited: list[Node] = []
    node = head
    while node is not None:
        if len(visited) == limit:
            return visited, False
        visited.append(node)
        node = node.next
    return visited, True


def ids(nodes: list[Node]) -> list[int]:
    return [id(node) for node in nodes]


def state(nodes: list[Node]) -> list[tuple[int, int]]:
    """Each node's value and the identity of its successor."""
    return [(node.val, id(node.next)) for node in nodes]


def digits_of(number: int) -> list[int]:
    """Digits of a non-negative integer, least significant first."""
    return [int(ch) for ch in reversed(str(number))]


def call(function, *args) -> object:
    """Call a function under test; report an exception instead of crashing."""
    try:
        return function(*args)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"


def run_fixtures() -> list[dict]:
    checks: list[dict] = []

    def record(name: str, expected: object, actual: object) -> None:
        checks.append(
            {
                "name": name,
                "expected": expected,
                "actual": actual,
                "passed": expected == actual,
            }
        )

    # Three distinct nodes A -> B -> C.
    a, b, c = Node(2), Node(4), Node(3)
    a.next = b
    b.next = c
    names = {id(a): "A", id(b): "B", id(c): "C"}

    def name_of(node: Node | None) -> str | None:
        return None if node is None else names.get(id(node), "other node")

    record("A.next is B (link)", "B", name_of(a.next))
    record("B.next is C (link)", "C", name_of(b.next))
    record("C.next is None (link)", None, name_of(c.next))
    record("values of A, B, C", [2, 4, 3], [a.val, b.val, c.val])
    visited, stopped = walk(a, 3)
    record("A->B->C traversal stops at None", True, stopped)
    record(
        "A->B->C traversal visits each node once, in order",
        ["A", "B", "C"],
        [name_of(node) for node in visited],
    )
    text = call(convert_to_str, a) if stopped else "skipped: traversal failed"
    record("convert_to_str(A) (values)", "243", text)
    record(
        "links after convert_to_str",
        ["B", "C", None],
        [name_of(a.next), name_of(b.next), name_of(c.next)],
    )

    # Smallest supported list: one node.
    only = Node(5)
    record("smallest list: next is None", True, only.next is None)
    record("smallest list: val", 5, only.val)
    visited, stopped = walk(only, 1)
    record(
        "smallest list: traversal visits it once", [True, 1], [stopped, len(visited)]
    )
    text = call(convert_to_str, only) if stopped else "skipped: traversal failed"
    record("smallest list: convert_to_str", "5", text)
    record("smallest list: next still None", True, only.next is None)

    # The sum 342 + 5 = 347 is built from new nodes.
    left, left_nodes = build([2, 4, 3])
    right = Node(5)
    inputs = left_nodes + [right]
    before = state(inputs)
    _, left_stopped = walk(left, 3)
    _, right_stopped = walk(right, 1)
    if left_stopped and right_stopped:
        head = call(add_two_numbers, left, right)
        result, stopped = walk(head, 4) if isinstance(head, Node) else ([], False)
        record("342 + 5: sum traversal stops at None", True, stopped)
        record("342 + 5: sum digits", [7, 4, 3], [node.val for node in result])
        record("342 + 5: sum nodes are distinct", 3, len(set(ids(result))))
        record(
            "342 + 5: input nodes reused in the sum",
            0,
            len(set(ids(result)) & set(ids(inputs))),
        )
    else:
        record("342 + 5: input traversal", True, False)
    record("342 + 5: inputs unchanged", True, state(inputs) == before)
    return checks


def generate_cases() -> list[dict]:
    """Readable small cases first, then seeded random cases."""
    cases = [
        {"kind": "readable", "left": left, "right": right}
        for left, right in READABLE_CASES
    ]
    rng = random.Random(SEED)
    for index in range(RANDOM_CASES):
        left = rng.randrange(10 ** rng.randint(1, 12))
        right = rng.randrange(10 ** rng.randint(1, 12))
        cases.append({"kind": "random", "index": index, "left": left, "right": right})
    return cases


def check_case(case: dict) -> dict:
    left_digits = digits_of(case["left"])
    right_digits = digits_of(case["right"])
    expected = digits_of(case["left"] + case["right"])
    left, left_nodes = build(left_digits)
    right, right_nodes = build(right_digits)
    inputs = left_nodes + right_nodes
    before = state(inputs)
    failures = []

    left_visited, left_stopped = walk(left, len(left_nodes))
    right_visited, right_stopped = walk(right, len(right_nodes))
    if not (left_stopped and ids(left_visited) == ids(left_nodes)):
        failures.append("left traversal")
    if not (right_stopped and ids(right_visited) == ids(right_nodes)):
        failures.append("right traversal")

    actual = None
    if not failures:  # never call module code on a list that may be cyclic
        if call(convert_to_str, left) != "".join(map(str, left_digits)):
            failures.append("convert_to_str value")
        head = call(add_two_numbers, left, right)
        if isinstance(head, Node):
            result, stopped = walk(head, len(expected) + 1)
            actual = [node.val for node in result]
            if not stopped:
                failures.append("sum traversal did not stop")
            if actual != expected:
                failures.append("sum digits")
            if len(set(ids(result))) != len(result):
                failures.append("a sum node appears twice")
            if set(ids(result)) & set(ids(inputs)):
                failures.append("the sum reuses an input node")
        else:
            failures.append(f"add_two_numbers {head}")
    if state(inputs) != before:
        failures.append("an input node changed")

    return {
        **case,
        "left_digits": left_digits,
        "right_digits": right_digits,
        "expected_sum_digits": expected,
        "actual_sum_digits": actual,
        "failures": failures,
        "passed": not failures,
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


def invariant_markdown(fixtures: list[dict], cases: list[dict]) -> str:
    passed_cases = sum(case["passed"] for case in cases)
    lines = [
        "# R24-T024 invariant of Node (add_two_numbers.py)",
        "",
        "## Invariant",
        "",
        "- `Node(x)` stores `x` in `val` and starts with `next` set to `None`, "
        "so one node is the smallest supported list.",
        "- Following `next` from the head of a list of distinct linked nodes "
        "visits each node exactly once and stops at `None`.",
        "- Ownership: the module's functions only read the nodes they are "
        "given and return lists built from new nodes.",
        "",
        "## Why it holds (source at bd1d152)",
        "",
        "- L19-21: `__init__` sets `val` and `next = None`; there is no other "
        "method, so a node only changes when a caller assigns to it.",
        "- L44-51: `add_two_numbers` only reads `left`/`right` (`.val`, "
        "`.next`) and moves its local variables along the lists.",
        "- L52, L55: every sum digit is a new `Node(...)`, linked in order, so "
        "the sum shares no node with its inputs and has no cycle.",
        "- L102-106: `convert_to_str` only reads `val` and follows `next`.",
        "",
        "## Generator domain",
        "",
        "The module docstring (L4-6) defines the domain as non-empty lists of "
        "digits for non-negative integers, least significant digit first. The "
        "generator draws non-negative integers with 1-12 digits from "
        f"`random.Random({SEED})` and turns each into its digits. That gives "
        "no empty lists, no leading zeros and only digits 0-9.",
        "",
        "## Result",
        "",
        f"- Fixtures: {sum(f['passed'] for f in fixtures)}/{len(fixtures)} "
        "checks passed.",
        f"- Property cases: {passed_cases}/{len(cases)} passed "
        f"({len(READABLE_CASES)} readable + {RANDOM_CASES} seeded).",
        "- Readable small case kept for review: 342 + 465 is 2->4->3 plus "
        "5->6->4, giving 7->0->8 from three new nodes.",
    ]
    return "\n".join(lines) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    fixtures = run_fixtures()
    cases = [check_case(case) for case in generate_cases()]
    pytest_result = run_pytest()
    failing = [case for case in cases if not case["passed"]]
    smallest = (
        min(
            failing,
            key=lambda c: (len(c["left_digits"]) + len(c["right_digits"]), c["left"]),
        )
        if failing
        else None
    )

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = ["R24-T024 Node invariant check (add_two_numbers.py)", ""]
    lines.append("Fixtures (expected vs actual):")
    for f in fixtures:
        lines.append(
            f"  [{mark(f['passed'])}] {f['name']}: expected={f['expected']} "
            f"actual={f['actual']}"
        )
    lines.append("")
    lines.append(
        f"Property cases: {len(cases) - len(failing)}/{len(cases)} passed "
        f"(seed {SEED}; {len(READABLE_CASES)} readable + {RANDOM_CASES} random)"
    )
    for case in cases[: len(READABLE_CASES)]:
        lines.append(
            f"  [{mark(case['passed'])}] readable {case['left']} + {case['right']}: "
            f"expected sum digits={case['expected_sum_digits']} "
            f"actual={case['actual_sum_digits']}"
        )
    if smallest:
        lines.append(
            f"  Smallest failing example: {smallest['left']} + {smallest['right']} "
            f"-> {smallest['failures']} (expected {smallest['expected_sum_digits']}, "
            f"actual {smallest['actual_sum_digits']})"
        )
    lines.append("")
    lines.append(f"Pytest command: {pytest_result['command']}")
    lines.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    lines.append(pytest_result["output"].rstrip())

    overall = (
        all(f["passed"] for f in fixtures)
        and not failing
        and len(cases) >= 100
        and pytest_result["ok"]
    )
    lines.append("")
    lines.append("OVERALL: " + mark(overall))
    report = "\n".join(lines) + "\n"

    write_json(
        "inputs.json",
        {
            "seed": SEED,
            "readable_cases": READABLE_CASES,
            "random_cases": RANDOM_CASES,
            "cases": generate_cases(),
        },
    )
    write_json("results.json", {"fixtures": fixtures, "property_cases": cases})
    write_json(
        "summary.json",
        {
            "task": "R24-T024",
            "target": "algorithms/linked_list/add_two_numbers.py:Node",
            "seed": SEED,
            "fixture_checks_passed": sum(f["passed"] for f in fixtures),
            "fixture_checks_total": len(fixtures),
            "property_cases_passed": len(cases) - len(failing),
            "property_cases_total": len(cases),
            "smallest_failing_example": smallest,
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "invariant.md").write_text(
        invariant_markdown(fixtures, cases), encoding="utf-8"
    )
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
