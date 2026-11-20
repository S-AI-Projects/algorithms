#!/usr/bin/env python3
"""Focused check runner for R24-T046: refactor of lowest_common_ancestor.

Refactored operation: deciding which way to go at the current node. The
original used chained comparisons (``p.val > root.val < q.val``); the new
code names the target range ``[low, high] = [min(p, q), max(p, q)]`` once
and compares the current key against it.

Checks:
1. Fixture (TreeNode BST from keys 4, 2, 6, 1, 3, 5, 7): explicit expected
   LCA keys for cases at the root and at leaves.
2. Before/after agreement: the original implementation (copied verbatim
   below as BEFORE) and the refactored function return the same node
   object for all 49 (p, q) pairs, for an empty tree, and for keys that
   are not in the tree.
3. The tree is not modified.
4. The focused pytest class with the project's pytest configuration:
   tests/test_tree.py::TestBstLowestCommonAncestor

Writes evidence to work/R24-T046/ and exits non-zero if any check fails.
The function has no external I/O, so nothing needs mocking.

Usage:
    python3 work/R24-T046/check.py
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
WORK = ROOT / "work" / "R24-T046"
sys.path.insert(0, str(ROOT))

from algorithms.common import TreeNode  # noqa: E402
from algorithms.tree.bst_lowest_common_ancestor import (  # noqa: E402
    lowest_common_ancestor as after,
)

PYTEST_TARGET = "tests/test_tree.py::TestBstLowestCommonAncestor"
KEYS = (4, 2, 6, 1, 3, 5, 7)


def before(root, p, q):
    """Original implementation at bd1d152, copied verbatim."""
    while root:
        if p.val > root.val < q.val:
            root = root.right
        elif p.val < root.val > q.val:
            root = root.left
        else:
            return root


# (p, q, expected LCA key, where the decision happens)
FIXTURE = [
    (1, 7, 4, "root: 1 <= 4 <= 7, split at the root"),
    (3, 5, 4, "root: 3 <= 4 <= 5, split at the root"),
    (4, 1, 4, "root: the root is one of the targets"),
    (1, 1, 1, "leaf: walks 4 -> 2 -> 1, range is [1, 1]"),
    (7, 7, 7, "leaf: walks 4 -> 6 -> 7, range is [7, 7]"),
    (1, 3, 2, "two leaves under 2"),
    (5, 7, 6, "two leaves under 6"),
    (3, 2, 2, "leaf and its parent"),
]


def insert(root, val):
    if root is None:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root


def build():
    root = None
    for key in KEYS:
        root = insert(root, key)
    nodes = {}
    stack = [root]
    while stack:
        node = stack.pop()
        if node is not None:
            nodes[node.val] = node
            stack.extend((node.left, node.right))
    return root, nodes


def shape(node):
    if node is None:
        return None
    return (node.val, id(node), shape(node.left), shape(node.right))


def key(node):
    return None if node is None else node.val


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

    log("R24-T046: lowest_common_ancestor refactor checks")
    root, nodes = build()
    original_shape = shape(root)

    fixture_results = []
    for p, q, expected, where in FIXTURE:
        actual = key(after(root, nodes[p], nodes[q]))
        ok = actual == expected
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [fixture] lca({p}, {q}) expected={expected} "
            f"actual={actual} ({where})"
        )
        fixture_results.append(
            {"p": p, "q": q, "expected": expected, "actual": actual, "where": where}
        )

    pair_results = []
    disagreements = 0
    for p in KEYS:
        for q in KEYS:
            old = before(root, nodes[p], nodes[q])
            new = after(root, nodes[p], nodes[q])
            same = old is new
            disagreements += not same
            pair_results.append([p, q, key(old), key(new), same])
    failures += disagreements > 0
    log(
        f"{'PASS' if disagreements == 0 else 'FAIL'} [before/after] 49 (p, q) "
        f"pairs return the same node: expected 0 disagreements, "
        f"actual {disagreements}"
    )

    edge_cases = [
        ("empty tree", None, TreeNode(1), TreeNode(2)),
        ("empty tree, no targets", None, None, None),
        ("keys above the tree", root, TreeNode(8), TreeNode(9)),
        ("keys below the tree", root, TreeNode(-2), TreeNode(-1)),
        ("keys straddling the root", root, TreeNode(0), TreeNode(8)),
    ]
    edge_results = []
    for label, tree, p, q in edge_cases:
        old, new = before(tree, p, q), after(tree, p, q)
        ok = old is new
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [before/after] {label}: "
            f"before={key(old)} after={key(new)}"
        )
        edge_results.append(
            {"case": label, "before": key(old), "after": key(new), "same": ok}
        )

    ok = shape(root) == original_shape
    failures += not ok
    log(f"{'PASS' if ok else 'FAIL'} [mutation] tree unchanged after all calls")

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
                "tree_keys_in_insert_order": list(KEYS),
                "fixture": [
                    {"p": p, "q": q, "expected": e, "where": w}
                    for p, q, e, w in FIXTURE
                ],
                "pairs": "all 49 (p, q) with p, q in the tree",
                "edge_cases": [label for label, *_ in edge_cases],
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "fixture": fixture_results,
                "before_after_pairs": {
                    "rows": "[p, q, before LCA key, after LCA key, same node]",
                    "disagreements": disagreements,
                    "results": pair_results,
                },
                "before_after_edge_cases": edge_results,
                "pytest": {
                    "command": f"python3 -m pytest {PYTEST_TARGET}",
                    "exit_code": proc.returncode,
                    "passed": passed,
                },
                "failures": failures,
            },
            indent=1,
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
