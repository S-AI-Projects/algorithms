#!/usr/bin/env python3
"""Focused check runner for R24-T050: mutation-resistant tests for topological_sort.

Invariant: the result contains every vertex exactly once (vertex
multiplicities preserved) and puts u before v for every edge (u, v),
counting repeated edges; the edge list is not modified.

1. Fixture on the real source, mapped from the task's sorting fixture to
   graphs: unsorted [3, 1, 2] -> chain 2->0->1; repeated value [2, 2, 1] ->
   repeated edge 1->0; ordered [1, 2, 3] -> chain 0->1->2; reversed
   [3, 2, 1] -> chain 2->1->0; smallest collection -> 0 and 1 vertices.
2. For each plausible one-line mutant (built in a temporary copy of the
   package, never in the repository):
   - the minimal input where original and mutant differ, with the correct
     output established independently (all valid orders by brute force);
   - the named regression test: passes on the original, fails on the mutant;
   - the existing TestTopologicalSort suite on the mutant, to show which
     mutants it missed.
3. The final source contains none of the mutant lines.
4. The focused pytest class on the real source:
   tests/test_graph.py::TestTopologicalSortMutationResistant

Writes evidence to work/R24-T050/ and exits non-zero if any check fails.
topological_sort has no external I/O, so nothing needs mocking.

Usage:
    python3 work/R24-T050/check.py
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import itertools
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T050"
SOURCE_REL = "algorithms/graph/topological_sort_bfs.py"
SOURCE = ROOT / SOURCE_REL
sys.path.insert(0, str(ROOT))

from algorithms.graph.topological_sort_bfs import topological_sort  # noqa: E402

CLASS = "tests/test_graph.py::TestTopologicalSortMutationResistant"
EXISTING = "tests/test_graph.py::TestTopologicalSort"

# (label, vertices, edges, expected order worked out by hand)
FIXTURE = [
    ("unsorted [3, 1, 2] -> chain 2->0->1", 3, [(2, 0), (0, 1)], [2, 0, 1]),
    ("repeated [2, 2, 1] -> edge 1->0 twice", 2, [(1, 0), (1, 0)], [1, 0]),
    ("ordered [1, 2, 3] -> chain 0->1->2", 3, [(0, 1), (1, 2)], [0, 1, 2]),
    ("reversed [3, 2, 1] -> chain 2->1->0", 3, [(2, 1), (1, 0)], [2, 1, 0]),
    ("smallest: no vertices", 0, [], []),
    ("smallest: one vertex", 1, [], [0]),
]

# (name, original line, mutant line, minimal input, named regression test)
MUTANTS = [
    (
        "skip a repeated edge when building the adjacency list",
        "        graph[u].append(v)\n",
        "        graph[u].append(v) if v not in graph[u] else None\n",
        (2, [(0, 1), (0, 1)]),
        "test_repeated_edge_is_counted_with_multiplicity",
    ),
    (
        "accumulation: in_degree[v] = 1 instead of += 1",
        "        in_degree[v] += 1\n",
        "        in_degree[v] = 1\n",
        (3, [(0, 2), (0, 1), (1, 2)]),
        "test_vertex_waits_for_all_predecessors",
    ),
    (
        "boundary: queue when in_degree <= 1 instead of == 0",
        "            if in_degree[neighbor] == 0:\n",
        "            if in_degree[neighbor] <= 1:\n",
        (2, [(0, 1), (0, 1)]),
        "test_repeated_edge_is_counted_with_multiplicity",
    ),
]


def outcome(func, vertices, edges):
    try:
        return func(vertices, list(edges))
    except ValueError as exc:
        return f"ValueError: {exc}"


def valid_orders(vertices, edges):
    """Independent oracle: every permutation that respects all edges."""
    return [
        list(order)
        for order in itertools.permutations(range(vertices))
        if all(order.index(u) < order.index(v) for u, v in edges)
    ]


def load_function(path):
    spec = importlib.util.spec_from_file_location(f"mutant_{path.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.topological_sort


def run_pytest(cwd, target):
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", target],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    passed = re.search(r"(\d+) passed", proc.stdout)
    failed = re.search(r"(\d+) failed", proc.stdout)
    reason = re.search(r"^E\s+(AssertionError: .*)$", proc.stdout, re.M)
    return {
        "exit_code": proc.returncode,
        "passed": int(passed.group(1)) if passed else 0,
        "failed": int(failed.group(1)) if failed else 0,
        "reason": reason.group(1) if reason else None,
    }


def make_mutant_tree(tmp, old, new):
    """Copy the package and the test file into tmp and apply one mutation."""
    shutil.copytree(ROOT / "algorithms", tmp / "algorithms")
    (tmp / "tests").mkdir()
    shutil.copy(ROOT / "tests" / "test_graph.py", tmp / "tests" / "test_graph.py")
    shutil.copy(ROOT / "pyproject.toml", tmp / "pyproject.toml")
    target = tmp / SOURCE_REL
    text = target.read_text()
    if text.count(old) != 1:
        return None
    target.write_text(text.replace(old, new))
    return target


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

    log("R24-T050: topological_sort mutation-resistance checks")

    fixture_results = []
    for label, vertices, edges, expected in FIXTURE:
        actual = outcome(topological_sort, vertices, edges)
        ok = actual == expected and actual in valid_orders(vertices, edges)
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [fixture] {label}: expected={expected} "
            f"actual={actual}"
        )
        fixture_results.append(
            {
                "case": label,
                "vertices": vertices,
                "edges": edges,
                "expected": expected,
                "actual": actual,
                "passed": ok,
            }
        )

    mutant_results = []
    for name, old, new, (vertices, edges), test in MUTANTS:
        named = f"{CLASS}::{test}"
        original_test = run_pytest(ROOT, named)
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            path = make_mutant_tree(tmp, old, new)
            if path is None:
                failures += 1
                log(f"FAIL [mutant] {name}: original line not found in source")
                mutant_results.append({"mutant": name, "error": "line not found"})
                continue
            mutant = load_function(path)
            mutant_test = run_pytest(tmp, named)
            existing = run_pytest(tmp, EXISTING)
        original = outcome(topological_sort, vertices, edges)
        mutated = outcome(mutant, vertices, edges)
        correct = valid_orders(vertices, edges)
        ok = (
            original in correct
            and mutated not in correct
            and original_test["exit_code"] == 0
            and mutant_test["exit_code"] != 0
        )
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [mutant] {name}: input "
            f"topological_sort({vertices}, {edges}) valid orders={correct}, "
            f"original={original}, mutant={mutated}"
        )
        log(
            f"    named test {test}: original exit={original_test['exit_code']} "
            f"(passed), mutant exit={mutant_test['exit_code']} "
            f"({mutant_test['reason']})"
        )
        log(
            f"    existing TestTopologicalSort on mutant: "
            f"{existing['passed']} passed, {existing['failed']} failed"
            + (
                " -> mutant NOT caught by the existing tests"
                if existing["exit_code"] == 0
                else ""
            )
        )
        mutant_results.append(
            {
                "mutant": name,
                "original_line": old.strip(),
                "mutant_line": new.strip(),
                "minimal_input": {"vertices": vertices, "edges": edges},
                "valid_orders": correct,
                "original_output": original,
                "mutant_output": mutated,
                "named_test": test,
                "named_test_on_original": original_test,
                "named_test_on_mutant": mutant_test,
                "existing_suite_on_mutant": existing,
                "caught": ok,
            }
        )

    source = SOURCE.read_text()
    leftovers = [new.strip() for _, _, new, _, _ in MUTANTS if new in source]
    ok = not leftovers
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [final source] no mutant line in "
        f"{SOURCE_REL}: leftovers={leftovers}"
    )

    final = run_pytest(ROOT, CLASS)
    ok = final["exit_code"] == 0 and final["passed"] > 0
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [pytest] python3 -m pytest {CLASS} "
        f"-> exit={final['exit_code']}, {final['passed']} passed"
    )

    log(f"RESULT: {'OK' if failures == 0 else f'{failures} FAILED'}")

    (WORK / "inputs.json").write_text(
        json.dumps(
            {
                "fixture": [
                    {"case": c, "vertices": v, "edges": e, "expected": x}
                    for c, v, e, x in FIXTURE
                ],
                "mutants": [
                    {
                        "mutant": n,
                        "original_line": o.strip(),
                        "mutant_line": m.strip(),
                        "minimal_input": {"vertices": i[0], "edges": i[1]},
                        "named_test": t,
                    }
                    for n, o, m, i, t in MUTANTS
                ],
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "fixture": fixture_results,
                "mutants": mutant_results,
                "pytest": {"command": f"python3 -m pytest {CLASS}", **final},
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
