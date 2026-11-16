"""Focused check for R24-T025: repeatable verification of remove_min.

Run from the repository root:

    python3 work/R24-T025/check.py

Dependency audit (step 2 of the issue): the module imports only
``from __future__ import annotations``, and ``remove_min`` refers only to
``len``, ``range``, ``pop`` and ``append`` (its ``__code__.co_names``). So it
reads no global state, files, network, clock or random numbers. The only
state is the list passed in, which is modified in place and returned.

It exits non-zero if any of these fails:

1. The dependency audit matches the expected imports and names above.
2. The fixture (push A, B, C; pop twice; push D; drain; pop order C, B, D,
   A), run three times: twice from fresh state and once after another valid
   input ([4, 8, 3, 7, 3] -> [4, 8, 7]). Every run must equal the same
   hand-calculated expected values, including the empty-state result.
3. Input isolation: calling remove_min on a copy changes only that copy, and
   an empty stack comes back as the same, still empty, list.
4. A sealed run: the fixture runs again with network sockets, file opening,
   the clock and random numbers patched to raise if anything touches them.
5. The focused regression tests (``TestRemoveMinRepeatable`` in
   ``tests/test_stack.py``), run with pytest using the project's pytest
   settings from ``pyproject.toml``. A run that collects zero tests counts as
   a failure.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, dependencies.md and check_output.txt.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
MODULE_PATH = REPO_ROOT / "algorithms" / "stack" / "remove_min.py"
sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test.
from algorithms.stack.remove_min import remove_min  # noqa: E402

TEST_NODE = "tests/test_stack.py::TestRemoveMinRepeatable"

# Fixture labels hold small integers so every input stays within list[int].
A, B, C, D = 3, 1, 2, 5

# Expected values calculated by hand before running the source.
EXPECTED = {
    "push A, B, C": [3, 2],
    "pop twice": [],
    "push D": [5],
    "drain": [],
    "pop order": [C, B, D, A],
}
OTHER_INPUT = [4, 8, 3, 7, 3]
OTHER_EXPECTED = [4, 8, 7]
ISOLATION_INPUT = [2, 8, 3, -6, 7, 3]
ISOLATION_EXPECTED = [2, 8, 3, 7, 3]
EXPECTED_IMPORTS = ["from __future__ import annotations"]
EXPECTED_NAMES = ["append", "len", "pop", "range"]


def call(function, *args) -> object:
    """Call the function under test; report an exception instead of crashing."""
    try:
        return function(*args)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"


def walk_fixture() -> dict:
    """Run the fixture once from fresh state and return what it saw."""
    stack: list[int] = []
    popped: list[int] = []
    seen: dict[str, object] = {}
    for value in (A, B, C):
        stack.append(value)
    seen["push A, B, C"] = call(remove_min, list(stack))
    popped.append(stack.pop())
    popped.append(stack.pop())
    seen["pop twice"] = call(remove_min, list(stack))
    stack.append(D)
    seen["push D"] = call(remove_min, list(stack))
    while stack:
        popped.append(stack.pop())
    seen["drain"] = call(remove_min, stack)
    seen["pop order"] = popped
    return seen


def compare(label: str, actual: dict) -> dict:
    rows = [
        {
            "state": key,
            "expected": expected,
            "actual": actual.get(key),
            "passed": actual.get(key) == expected,
        }
        for key, expected in EXPECTED.items()
    ]
    return {"run": label, "rows": rows, "passed": all(r["passed"] for r in rows)}


def audit_dependencies() -> dict:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            names = ", ".join(alias.name for alias in node.names)
            imports.append(f"from {node.module} import {names}")
        elif isinstance(node, ast.Import):
            imports.append("import " + ", ".join(a.name for a in node.names))
    names = sorted(set(remove_min.__code__.co_names))
    return {
        "imports": imports,
        "expected_imports": EXPECTED_IMPORTS,
        "names_used_by_remove_min": names,
        "expected_names": EXPECTED_NAMES,
        "passed": imports == EXPECTED_IMPORTS and names == EXPECTED_NAMES,
    }


def sealed_walk() -> dict:
    """Run the fixture with outside resources patched to raise if touched."""

    def forbid(what: str):
        def _raise(*args, **kwargs):
            raise AssertionError(f"remove_min touched {what}")

        return _raise

    # builtins.open goes last, so patching the others never needs a file.
    targets = {
        "socket.socket": "the network",
        "time.time": "the clock",
        "time.monotonic": "the clock",
        "time.perf_counter": "the clock",
        "random.random": "random numbers",
        "random.randrange": "random numbers",
        "random.choice": "random numbers",
        "random.shuffle": "random numbers",
        "builtins.open": "a file",
    }
    with contextlib.ExitStack() as patches:
        for target, what in targets.items():
            patches.enter_context(mock.patch(target, side_effect=forbid(what)))
        return walk_fixture()


def run_isolation() -> list[dict]:
    original = list(ISOLATION_INPUT)
    working_copy = list(original)
    result = call(remove_min, working_copy)
    empty: list[int] = []
    empty_result = call(remove_min, empty)
    return [
        {
            "name": "copy is changed in place and returned",
            "expected": [True, ISOLATION_EXPECTED],
            "actual": [result is working_copy, working_copy],
        },
        {
            "name": "original list is untouched",
            "expected": ISOLATION_INPUT,
            "actual": original,
        },
        {
            "name": "empty stack comes back as the same empty list",
            "expected": [True, []],
            "actual": [empty_result is empty, empty],
        },
    ]


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


def dependencies_markdown(audit: dict, sealed: dict) -> str:
    lines = [
        "# R24-T025 dependency audit for remove_min",
        "",
        "Observable dependencies: **none**.",
        "",
        f"- Module imports: {audit['imports']} (expected {audit['expected_imports']}).",
        f"- Names used by `remove_min` (`__code__.co_names`): "
        f"{audit['names_used_by_remove_min']} "
        f"(expected {audit['expected_names']}).",
        "- So the function reads no global state, files, network, clock or "
        "random numbers. The only state is the list passed in, which is "
        "modified in place and returned (documented in its docstring).",
        "- Sealed run (network, files, clock and random numbers patched to "
        f"raise): {'PASS' if sealed['passed'] else 'FAIL'}.",
        "",
        "No dependency seam was added, because there is no dependency to "
        "inject. The public interface is unchanged.",
    ]
    return "\n".join(lines) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    audit = audit_dependencies()
    run_1 = compare("run 1, fresh state", walk_fixture())
    run_2 = compare("run 2, fresh state", walk_fixture())
    other = list(OTHER_INPUT)
    other_result = call(remove_min, other)
    run_3 = compare("run 3, after another valid input", walk_fixture())
    other_check = {
        "name": "other input [4, 8, 3, 7, 3] before run 3, and unchanged after",
        "expected": [OTHER_EXPECTED, OTHER_EXPECTED],
        "actual": [other_result, other],
    }
    sealed = compare("sealed run", sealed_walk())
    isolation = run_isolation() + [other_check]
    for item in isolation:
        item["passed"] = item["expected"] == item["actual"]
    pytest_result = run_pytest()

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = ["R24-T025 remove_min repeatability check", ""]
    lines.append(
        f"[{mark(audit['passed'])}] dependency audit: imports={audit['imports']} "
        f"names={audit['names_used_by_remove_min']}"
    )
    lines.append("")
    for run in (run_1, run_2, run_3, sealed):
        lines.append(f"[{mark(run['passed'])}] fixture {run['run']}:")
        for row in run["rows"]:
            lines.append(
                f"    [{mark(row['passed'])}] {row['state']}: "
                f"expected={row['expected']} actual={row['actual']}"
            )
    lines.append("")
    lines.append("Input isolation:")
    for item in isolation:
        lines.append(
            f"  [{mark(item['passed'])}] {item['name']}: "
            f"expected={item['expected']} actual={item['actual']}"
        )
    lines.append("")
    lines.append(f"Pytest command: {pytest_result['command']}")
    lines.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    lines.append(pytest_result["output"].rstrip())

    runs = [run_1, run_2, run_3, sealed]
    overall = (
        audit["passed"]
        and all(run["passed"] for run in runs)
        and all(item["passed"] for item in isolation)
        and pytest_result["ok"]
    )
    lines.append("")
    lines.append("OVERALL: " + mark(overall))
    report = "\n".join(lines) + "\n"

    write_json(
        "inputs.json",
        {
            "fixture": "push A, B, C; pop twice; push D; drain",
            "values": {"A": A, "B": B, "C": C, "D": D},
            "expected": EXPECTED,
            "other_valid_input": OTHER_INPUT,
            "isolation_input": ISOLATION_INPUT,
        },
    )
    write_json(
        "results.json",
        {"dependency_audit": audit, "runs": runs, "isolation": isolation},
    )
    write_json(
        "summary.json",
        {
            "task": "R24-T025",
            "target": "algorithms/stack/remove_min.py:remove_min",
            "dependencies_found": [] if audit["passed"] else audit,
            "fixture_runs_passed": sum(run["passed"] for run in runs),
            "fixture_runs_total": len(runs),
            "isolation_checks_passed": sum(item["passed"] for item in isolation),
            "isolation_checks_total": len(isolation),
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "dependencies.md").write_text(
        dependencies_markdown(audit, sealed), encoding="utf-8"
    )
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
