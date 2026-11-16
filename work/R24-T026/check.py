"""Focused check for R24-T026: one readability refactor in huffman_coding.Node.

Run from the repository root:

    python3 work/R24-T026/check.py

The refactor: ``Node.__str__`` and ``Node.__repr__`` built the same text
``<ch: {sign}: {frequency}>`` twice (L47-51 at the pinned commit). Now the
format is written once in ``__repr__``, and ``__str__ = __repr__`` states that
both show the same text. No algorithm, return type, ordering, side effect or
public argument changed.

It exits non-zero if any of these fails:

1. Every fixture observation on the refactored Node equals its hand-calculated
   expected value. Each one names the source line that establishes its
   precondition.
2. Before/after agreement: the same observations on the original Node, loaded
   from the pinned commit with ``git show``, are identical.
3. Scope: compared with the pinned commit, the only changed file under
   ``algorithms/`` is ``huffman_coding.py``, its diff is a single hunk, and
   ``Node.__str__ is Node.__repr__`` after the change.
4. The focused tests (``TestHuffmanNode`` in ``tests/test_compression.py``),
   run with pytest using the project's pytest settings from ``pyproject.toml``.
   A run that collects zero tests counts as a failure.

Node does no I/O. The check reads the pinned source through git, and nothing
else is touched.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, refactor_diff.txt and check_output.txt.
"""

from __future__ import annotations

import difflib
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test.
from algorithms.compression.huffman_coding import Node  # noqa: E402

PINNED = "bd1d152f9ec7331c69be662831610b003b10fc7a"
SOURCE = "algorithms/compression/huffman_coding.py"
TEST_NODE = "tests/test_compression.py::TestHuffmanNode"


def observe_internal(node_class: type) -> dict:
    left = node_class(frequency=2, sign=98)
    right = node_class(frequency=3, sign=99)
    parent = node_class(frequency=5, left=left, right=right)
    return {
        "links": [parent.left is left, parent.right is right],
        "sign": parent.sign,
        "str": str(parent),
        "repr": repr(parent),
        "str of [left, right]": str([left, right]),
    }


# (name, how to observe it, expected value, source line for the precondition)
# Line numbers refer to huffman_coding.py at the pinned commit bd1d152.
CASES = [
    (
        "smallest valid input: Node() fields",
        lambda n: [n().frequency, n().sign, n().left, n().right],
        [0, None, None, None],
        "L24-30: every parameter has a default (frequency=0 L26, sign=None "
        "L27, left=None L28, right=None L29)",
    ),
    (
        "smallest valid input: str(Node())",
        lambda n: str(n()),
        "<ch: None: 0>",
        "L47-48: __str__ formats sign and frequency",
    ),
    (
        "smallest valid input: repr(Node())",
        lambda n: repr(n()),
        "<ch: None: 0>",
        "L50-51: __repr__ formats sign and frequency",
    ),
    (
        "ordinary leaf: Node(frequency=5, sign=97) fields",
        lambda n: [
            n(frequency=5, sign=97).frequency,
            n(frequency=5, sign=97).sign,
            n(frequency=5, sign=97).left,
            n(frequency=5, sign=97).right,
        ],
        [5, 97, None, None],
        "L26-27: frequency is an int and sign an int or None; L31-34 store them",
    ),
    (
        "ordinary leaf: str and repr",
        lambda n: [str(n(frequency=5, sign=97)), repr(n(frequency=5, sign=97))],
        ["<ch: 97: 5>", "<ch: 97: 5>"],
        "L47-51: the text form <ch: {sign}: {frequency}>",
    ),
    (
        "ordinary internal node: Node(5, left=..., right=...)",
        observe_internal,
        {
            "links": [True, True],
            "sign": None,
            "str": "<ch: None: 5>",
            "repr": "<ch: None: 5>",
            "str of [left, right]": "[<ch: 98: 2>, <ch: 99: 3>]",
        },
        "L28-29, L33-34: left and right are stored as given; L27: sign "
        "defaults to None; L47-51: text form",
    ),
    (
        "ordering: low < high, high < low, high > low, low > high",
        lambda n: [
            n(frequency=2, sign=1) < n(frequency=7, sign=2),
            n(frequency=7, sign=2) < n(frequency=2, sign=1),
            n(frequency=7, sign=2) > n(frequency=2, sign=1),
            n(frequency=2, sign=1) > n(frequency=7, sign=2),
        ],
        [True, False, True, False],
        "L36-40: __lt__ and __gt__ compare frequency only",
    ),
    (
        "equality: same frequency, different frequency, non-Node",
        lambda n: [
            n(frequency=4, sign=1) == n(frequency=4, sign=2),
            n(frequency=4) == n(frequency=5),
            n(frequency=4) == 4,
        ],
        [True, False, False],
        "L42-45: __eq__ compares frequency only and returns NotImplemented "
        "for a non-Node (L43-44)",
    ),
]


def safe(observe, node_class: type) -> object:
    try:
        return observe(node_class)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def load_before() -> tuple[type, str]:
    """Load Node from the pinned commit without touching the working tree."""
    source = git("show", f"{PINNED}:{SOURCE}")
    module = types.ModuleType("huffman_coding_before")
    exec(compile(source, f"{SOURCE}@{PINNED[:7]}", "exec"), module.__dict__)
    return module.Node, source


def scope_check(before_source: str) -> dict:
    after_source = (REPO_ROOT / SOURCE).read_text(encoding="utf-8")
    diff = list(
        difflib.unified_diff(
            before_source.splitlines(keepends=True),
            after_source.splitlines(keepends=True),
            fromfile=f"{SOURCE}@{PINNED[:7]}",
            tofile=f"{SOURCE} (this branch)",
        )
    )
    hunks = sum(1 for line in diff if line.startswith("@@"))
    changed = sorted(
        line.split("\t")[-1]
        for line in git("diff", "--numstat", PINNED, "--", "algorithms/").splitlines()
    )
    return {
        "diff": "".join(diff),
        "hunks": hunks,
        "changed_files_under_algorithms": changed,
        "str_is_repr_after": Node.__str__ is Node.__repr__,
        "passed": hunks == 1 and changed == [SOURCE] and Node.__str__ is Node.__repr__,
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
        "git": git("--version").strip(),
    }


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    before_node, before_source = load_before()
    results = []
    for name, observe, expected, precondition in CASES:
        before = safe(observe, before_node)
        after = safe(observe, Node)
        results.append(
            {
                "name": name,
                "precondition_source_line": precondition,
                "expected": expected,
                "before": before,
                "after": after,
                "after_matches_expected": after == expected,
                "before_after_agree": before == after,
                "passed": after == expected and before == after,
            }
        )
    scope = scope_check(before_source)
    pytest_result = run_pytest()

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = ["R24-T026 Node refactor check (huffman_coding.py)", ""]
    lines.append("Fixture observations (expected / before / after):")
    for r in results:
        lines.append(f"  [{mark(r['passed'])}] {r['name']}")
        lines.append(f"      precondition: {r['precondition_source_line']}")
        lines.append(
            f"      expected={r['expected']!r} before={r['before']!r} "
            f"after={r['after']!r}"
        )
    lines.append("")
    lines.append(
        f"[{mark(scope['passed'])}] scope: changed files under algorithms/ = "
        f"{scope['changed_files_under_algorithms']}, hunks = {scope['hunks']}, "
        f"Node.__str__ is Node.__repr__ = {scope['str_is_repr_after']}"
    )
    lines.append("")
    lines.append(f"Pytest command: {pytest_result['command']}")
    lines.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    lines.append(pytest_result["output"].rstrip())

    overall = (
        all(r["passed"] for r in results) and scope["passed"] and pytest_result["ok"]
    )
    lines.append("")
    lines.append("OVERALL: " + mark(overall))
    report = "\n".join(lines) + "\n"

    write_json(
        "inputs.json",
        {
            "pinned_commit": PINNED,
            "cases": [
                {"name": name, "expected": expected, "precondition_source_line": pre}
                for name, _, expected, pre in CASES
            ],
        },
    )
    write_json("results.json", {"observations": results, "scope": scope})
    write_json(
        "summary.json",
        {
            "task": "R24-T026",
            "target": "algorithms/compression/huffman_coding.py:Node",
            "refactor": "__str__ = __repr__: the text form is written once",
            "observations_passed": sum(r["passed"] for r in results),
            "observations_total": len(results),
            "before_after_agree": all(r["before_after_agree"] for r in results),
            "scope_passed": scope["passed"],
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "refactor_diff.txt").write_text(scope["diff"], encoding="utf-8")
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
