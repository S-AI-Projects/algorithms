#!/usr/bin/env python3
"""Focused check runner for R24-T044: invariant of reverse_list.

Invariant: for input n0 -> n1 -> ... -> nk, reverse_list returns the same
node objects linked nk -> ... -> n0 -> None. Traversal terminates, every
input node appears exactly once, no value changes, and the old head becomes
the tail. Links are compared by node identity and values separately.

1. Fixture: three distinct nodes A -> B -> C, plus the smallest supported
   lists (None and a single node).
2. 200 seeded cases (seed 44): finite, acyclic ListNode chains of length
   0..25 with values in -3..3, starting with the readable case [1, 2, 3].
3. Mutation check: three broken versions of reverse_list are built from a
   temporary copy of the source. The invariant must reject each one, and
   the smallest failing case is reported.
4. Runs the focused pytest class with the project's pytest configuration:
   tests/test_linked_list.py::TestReverseListInvariant

Writes evidence to work/R24-T044/ and exits non-zero if any check fails.
reverse_list has no external I/O, so nothing needs mocking.

Usage:
    python3 work/R24-T044/check.py
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import platform
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T044"
SOURCE = ROOT / "algorithms" / "linked_list" / "reverse.py"
sys.path.insert(0, str(ROOT))

from algorithms.common import ListNode  # noqa: E402
from algorithms.linked_list.reverse import reverse_list  # noqa: E402

PYTEST_TARGET = "tests/test_linked_list.py::TestReverseListInvariant"
SEED = 44
CASES = 200

LOOP = """    prev = None
    while head:
        current = head
        head = head.next
        current.next = prev
        prev = current
    return prev
"""

# (name, text to replace in reverse.py, replacement)
MUTANTS = [
    (
        "drop links (current.next = None)",
        "        current.next = prev\n",
        "        current.next = None\n",
    ),
    (
        "skip last node (while head.next)",
        "    while head:\n        current = head\n",
        "    while head.next:\n        current = head\n",
    ),
    (
        "reverse values only, keep links",
        LOOP,
        """    nodes = []
    while head:
        nodes.append(head)
        head = head.next
    values = [node.val for node in nodes]
    for node, value in zip(nodes, reversed(values)):
        node.val = value
    return nodes[0]
""",
    ),
]


def build(values):
    nodes = [ListNode(v) for v in values]
    for node, nxt in zip(nodes, nodes[1:], strict=False):
        node.next = nxt
    return (nodes[0] if nodes else None), nodes


def walk(head, limit):
    seen = []
    while head is not None:
        if len(seen) == limit + 1:
            return None
        seen.append(head)
        head = head.next
    return seen


def violation(reverse, values):
    head, nodes = build(values)
    walked = walk(reverse(head), len(nodes))
    if walked is None:
        return "traversal did not terminate"
    if len(walked) != len(nodes):
        return f"expected {len(nodes)} nodes, reached {len(walked)}"
    if any(a is not b for a, b in zip(walked, reversed(nodes), strict=True)):
        return "result is not the original nodes in reverse order"
    if [node.val for node in walked] != list(reversed(values)):
        return "node values changed"
    if nodes and nodes[0].next is not None:
        return "old head is not the tail"
    return None


def seeded_cases():
    rng = random.Random(SEED)
    cases = [[1, 2, 3]]
    while len(cases) < CASES:
        length = rng.randint(0, 25)
        cases.append([rng.randint(-3, 3) for _ in range(length)])
    return cases


def smallest_failure(reverse, cases):
    failures = []
    for values in cases:
        problem = violation(reverse, values)
        if problem is not None:
            failures.append({"values": values, "problem": problem})
    smallest = min(failures, key=lambda f: len(f["values"]), default=None)
    return len(failures), smallest


def load_mutant(name, old, new, tmp):
    text = SOURCE.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"mutant {name!r}: source pattern not found once")
    path = Path(tmp) / f"reverse_mutant_{abs(hash(name))}.py"
    path.write_text(text.replace(old, new))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.reverse_list


def fixture_checks():
    a, b, c = ListNode("A"), ListNode("B"), ListNode("C")
    a.next, b.next = b, c
    result = reverse_list(a)
    single = ListNode(1)
    single_result = reverse_list(single)
    return [
        ("A->B->C: returned head is C", result is c, True),
        ("A->B->C link: C.next is B", c.next is b, True),
        ("A->B->C link: B.next is A", b.next is a, True),
        ("A->B->C link: A.next is None", a.next is None, True),
        ("A->B->C values", [n.val for n in walk(result, 3)], ["C", "B", "A"]),
        ("empty list: reverse_list(None)", reverse_list(None), None),
        ("single node: same node returned", single_result is single, True),
        ("single node: next is None", single.next is None, True),
    ]


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

    log("R24-T044: reverse_list invariant checks")

    fixture_results = []
    for label, actual, expected in fixture_checks():
        ok = actual == expected
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [fixture] {label}: expected={expected!r} "
            f"actual={actual!r}"
        )
        fixture_results.append(
            {"check": label, "expected": expected, "actual": actual, "passed": ok}
        )

    cases = seeded_cases()
    lengths = [len(c) for c in cases]
    count, smallest = smallest_failure(reverse_list, cases)
    ok = count == 0
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [property] {len(cases)} seeded cases "
        f"(seed={SEED}, lengths {min(lengths)}..{max(lengths)}): "
        f"expected 0 violations, actual {count}"
        + (f"; smallest failing case {smallest}" if smallest else "")
    )

    mutant_results = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, old, new in MUTANTS:
            try:
                broken = load_mutant(name, old, new, tmp)
            except RuntimeError as exc:
                failures += 1
                log(f"FAIL [mutant] {name}: could not build mutant ({exc})")
                mutant_results.append({"mutant": name, "error": str(exc)})
                continue
            count_m, smallest_m = smallest_failure(broken, cases)
            ok = count_m > 0
            failures += not ok
            log(
                f"{'PASS' if ok else 'FAIL'} [mutant] {name}: expected violations, "
                f"actual {count_m}/{len(cases)}; smallest failing case {smallest_m}"
            )
            mutant_results.append(
                {
                    "mutant": name,
                    "violations": count_m,
                    "cases": len(cases),
                    "smallest_failing_case": smallest_m,
                    "caught": ok,
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
            {
                "fixture": "A -> B -> C (values 'A', 'B', 'C'), None, ListNode(1)",
                "generator": {
                    "seed": SEED,
                    "cases": CASES,
                    "length": "0..25",
                    "values": "-3..3",
                    "first_case": [1, 2, 3],
                },
                "cases": cases,
                "mutants": [name for name, _, _ in MUTANTS],
            },
            indent=1,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "fixture": fixture_results,
                "property": {
                    "cases": len(cases),
                    "expected_violations": 0,
                    "actual_violations": count,
                    "smallest_failing_case": smallest,
                },
                "mutants": mutant_results,
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
    (WORK / "check_output.txt").write_text("\n".join(lines) + "\n")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
