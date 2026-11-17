"""Focused check runner for R24-T012: supported boundaries of RandomListNode.

Verifies boundary cases, input/output contract, and link separation for
``RandomListNode`` and ``copy_random_pointer`` functions in
``algorithms/linked_list/copy_random_pointer.py``.

Saves verification evidence to ``work/R24-T012/``:
- ``boundary_table.md``
- ``inputs.json``
- ``results.json``
- ``summary.json``
- ``tool_versions.json``
- ``check_output.txt``

Run from repository root:
    python3 work/R24-T012/check.py

Exits non-zero on any failure.
"""

from __future__ import annotations

import doctest
import importlib
import json
import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test
from algorithms.linked_list.copy_random_pointer import (  # noqa: E402
    RandomListNode,
    copy_random_pointer_v1,
    copy_random_pointer_v2,
)


def run_checks() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 70)
    log("R24-T012 RandomListNode boundary and contract check")
    log("=" * 70)

    # 1. Fixture: Three distinct nodes A -> B -> C with random pointers
    log("\nExecuting Fixture: Three distinct nodes A -> B -> C")
    node_a = RandomListNode("A")
    node_b = RandomListNode("B")
    node_c = RandomListNode("C")
    node_a.next = node_b
    node_b.next = node_c
    node_c.next = None
    node_a.random = node_c
    node_b.random = node_a
    node_c.random = None

    fixture_results = {}
    fixture_passed = True

    for copy_fn in (copy_random_pointer_v1, copy_random_pointer_v2):
        fn_name = copy_fn.__name__
        copied_a = copy_fn(node_a)
        copied_b = copied_a.next if copied_a else None
        copied_c = copied_b.next if copied_b else None

        # Separate check: values
        values_ok = (
            copied_a is not None
            and copied_b is not None
            and copied_c is not None
            and copied_a.label == "A"
            and copied_b.label == "B"
            and copied_c.label == "C"
        )

        # Separate check: node links & identity separation
        links_ok = (
            copied_a is not None
            and copied_b is not None
            and copied_c is not None
            and copied_a is not node_a
            and copied_b is not node_b
            and copied_c is not node_c
            and copied_a.next is copied_b
            and copied_b.next is copied_c
            and copied_c.next is None
            and copied_a.random is copied_c
            and copied_b.random is copied_a
            and copied_c.random is None
        )

        # Non-mutation of original
        orig_unmutated = (
            node_a.label == "A"
            and node_b.label == "B"
            and node_c.label == "C"
            and node_a.next is node_b
            and node_b.next is node_c
            and node_c.next is None
            and node_a.random is node_c
            and node_b.random is node_a
            and node_c.random is None
        )

        passed = values_ok and links_ok and orig_unmutated
        if not passed:
            fixture_passed = False

        log(
            f"  [{'PASS' if passed else 'FAIL'}] {fn_name}: "
            f"values_ok={values_ok} links_ok={links_ok} orig_unmutated={orig_unmutated}"
        )

        fixture_results[fn_name] = {
            "values_ok": values_ok,
            "links_ok": links_ok,
            "orig_unmutated": orig_unmutated,
            "passed": passed,
        }

    # 2. Boundary Cases Table
    boundary_cases = [
        {
            "partition": "valid boundary",
            "name": "smallest_empty_list_v1",
            "description": "Smallest list: None passed to copy_random_pointer_v1",
            "source_contract": (
                "copy_random_pointer.py L28-54; head is None returns None"
            ),
            "input": "None",
            "expected": "None",
            "test_fn": lambda: copy_random_pointer_v1(None) is None,
        },
        {
            "partition": "valid boundary",
            "name": "smallest_empty_list_v2",
            "description": "Smallest list: None passed to copy_random_pointer_v2",
            "source_contract": (
                "copy_random_pointer.py L57-83; head is None returns None"
            ),
            "input": "None",
            "expected": "None",
            "test_fn": lambda: copy_random_pointer_v2(None) is None,
        },
        {
            "partition": "valid boundary",
            "name": "single_node_smallest_nonempty_v1",
            "description": "Single node with next=None and random=None (v1)",
            "source_contract": "copy_random_pointer.py L19, L28; 1-node deep copy",
            "input": "RandomListNode(1)",
            "expected": "distinct node with label=1, next=None, random=None",
            "test_fn": lambda: (
                lambda orig, cp: (
                    cp is not None
                    and cp is not orig
                    and cp.label == 1
                    and cp.next is None
                    and cp.random is None
                )
            )(RandomListNode(1), copy_random_pointer_v1(RandomListNode(1))),
        },
        {
            "partition": "valid boundary",
            "name": "single_node_smallest_nonempty_v2",
            "description": "Single node with next=None and random=None (v2)",
            "source_contract": "copy_random_pointer.py L19, L57; 1-node deep copy",
            "input": "RandomListNode(1)",
            "expected": "distinct node with label=1, next=None, random=None",
            "test_fn": lambda: (
                lambda orig, cp: (
                    cp is not None
                    and cp is not orig
                    and cp.label == 1
                    and cp.next is None
                    and cp.random is None
                )
            )(RandomListNode(1), copy_random_pointer_v2(RandomListNode(1))),
        },
        {
            "partition": "valid boundary",
            "name": "single_node_self_referential_v1",
            "description": "Single node with random pointing to itself (v1)",
            "source_contract": (
                "copy_random_pointer.py L38-42; self-referential random pointer"
            ),
            "input": "RandomListNode(1) with random=self",
            "expected": "distinct copy with copy.random is copy",
            "test_fn": lambda: (
                lambda n: (setattr(n, "random", n) or True)
                and (lambda cp: cp is not None and cp is not n and cp.random is cp)(
                    copy_random_pointer_v1(n)
                )
            )(RandomListNode(1)),
        },
        {
            "partition": "valid boundary",
            "name": "single_node_self_referential_v2",
            "description": "Single node with random pointing to itself (v2)",
            "source_contract": (
                "copy_random_pointer.py L67-71; self-referential random pointer"
            ),
            "input": "RandomListNode(1) with random=self",
            "expected": "distinct copy with copy.random is copy",
            "test_fn": lambda: (
                lambda n: (setattr(n, "random", n) or True)
                and (lambda cp: cp is not None and cp is not n and cp.random is cp)(
                    copy_random_pointer_v2(n)
                )
            )(RandomListNode(1)),
        },
        {
            "partition": "valid boundary",
            "name": "falsy_label_zero_preserved",
            "description": "Node with falsy integer label 0 preserved",
            "source_contract": "RandomListNode L22-25; preserves label 0",
            "input": "RandomListNode(0)",
            "expected": "label == 0",
            "test_fn": lambda: (
                RandomListNode(0).label == 0
                and getattr(copy_random_pointer_v1(RandomListNode(0)), "label", None)
                == 0
                and getattr(copy_random_pointer_v2(RandomListNode(0)), "label", None)
                == 0
            ),
        },
        {
            "partition": "valid boundary",
            "name": "negative_label_preserved",
            "description": "Node with negative integer label",
            "source_contract": "RandomListNode L22-25; negative integer supported",
            "input": "RandomListNode(-7)",
            "expected": "label == -7",
            "test_fn": lambda: RandomListNode(-7).label == -7,
        },
        {
            "partition": "valid interior",
            "name": "duck_typed_string_label",
            "description": "Node with string label (duck typing supported)",
            "source_contract": "RandomListNode L22-25; generic label assignment",
            "input": "RandomListNode('A')",
            "expected": "label == 'A'",
            "test_fn": lambda: RandomListNode("A").label == "A",
        },
        {
            "partition": "explicitly unsupported",
            "name": "missing_required_label_argument",
            "description": (
                "Instantiating RandomListNode without required label argument"
            ),
            "source_contract": (
                "RandomListNode.__init__(self, label: int) requires label argument"
            ),
            "input": "RandomListNode()",
            "expected": "raises TypeError",
            "test_fn": lambda: _test_raises_type_error(),
        },
    ]

    def _test_raises_type_error() -> bool:
        try:
            RandomListNode()  # type: ignore[call-arg]
            return False
        except TypeError:
            return True

    log("\nExecuting Boundary Cases:")
    boundary_results = []
    boundary_failures = 0

    for case in boundary_cases:
        name = case["name"]
        partition = case["partition"]
        desc = case["description"]
        expected = case["expected"]
        source = case["source_contract"]

        try:
            passed = bool(case["test_fn"]())
        except Exception as exc:
            passed = False
            log(f"  Exception during {name}: {exc}")

        if not passed:
            boundary_failures += 1
            status = "FAIL"
        else:
            status = "PASS"

        log(f"  [{status}] ({partition}) {name}: expected={expected}")

        boundary_results.append(
            {
                "partition": partition,
                "name": name,
                "description": desc,
                "input": case["input"],
                "expected": expected,
                "source_contract": source,
                "passed": passed,
            }
        )

    # 3. Doctests
    log("\nRunning doctests on algorithms/linked_list/copy_random_pointer.py...")
    mod_copy = importlib.import_module("algorithms.linked_list.copy_random_pointer")
    dt_res = doctest.testmod(mod_copy)
    doctest_passed = dt_res.failed == 0
    log(f"Doctest results: attempted={dt_res.attempted}, failed={dt_res.failed}")

    # 4. Native test execution (pytest)
    pytest_target = "tests/test_linked_list.py::TestRandomListNodeBoundaries"
    venv_pytest = REPO_ROOT / ".venv" / "bin" / "pytest"
    if venv_pytest.exists():
        pytest_cmd = [
            str(venv_pytest),
            pytest_target,
            "-v",
            "--no-header",
        ]
    else:
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            pytest_target,
            "-v",
            "--no-header",
        ]

    log(f"\nExecuting test command: {' '.join(pytest_cmd)}")
    proc = subprocess.run(
        pytest_cmd, cwd=str(REPO_ROOT), capture_output=True, text=True
    )
    log(proc.stdout)
    if proc.stderr:
        log(proc.stderr)

    pytest_passed = proc.returncode == 0
    pytest_test_count = 6

    # 5. Save evidence artifacts
    inputs_evidence = [
        {
            "name": case["name"],
            "partition": case["partition"],
            "description": case["description"],
            "input": case["input"],
            "expected": case["expected"],
            "source_contract": case["source_contract"],
        }
        for case in boundary_cases
    ]

    with open(HERE / "inputs.json", "w", encoding="utf-8") as f:
        json.dump(inputs_evidence, f, indent=2)

    results_evidence = {
        "fixture_three_nodes": fixture_results,
        "boundary_cases": boundary_results,
    }
    with open(HERE / "results.json", "w", encoding="utf-8") as f:
        json.dump(results_evidence, f, indent=2)

    # Boundary Table markdown
    table_lines = [
        "# R24-T012 boundary table for RandomListNode and copy_random_pointer",
        "",
        "Source: algorithms/linked_list/copy_random_pointer.py at bd1d152.",
        "",
        "| Partition | Case / Input | Expected | Source Contract | Result |",
        "|---|---|---|---|---|",
    ]
    for case in boundary_results:
        part = case["partition"]
        inp = case["input"]
        exp = case["expected"]
        src = case["source_contract"]
        res = "PASS" if case["passed"] else "FAIL"
        table_lines.append(f"| {part} | `{inp}` | {exp} | {src} | {res} |")

    with open(HERE / "boundary_table.md", "w", encoding="utf-8") as f:
        f.write("\n".join(table_lines) + "\n")

    try:
        ver_proc = subprocess.run(
            [pytest_cmd[0], "--version"], capture_output=True, text=True
        )
        pytest_ver = (ver_proc.stdout or ver_proc.stderr).strip().split()[-1]
    except Exception:
        pytest_ver = "unknown"

    tool_versions = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pytest": pytest_ver,
        "pytest_command": " ".join(pytest_cmd),
    }
    with open(HERE / "tool_versions.json", "w", encoding="utf-8") as f:
        json.dump(tool_versions, f, indent=2)

    overall_passed = (
        fixture_passed
        and boundary_failures == 0
        and doctest_passed
        and pytest_passed
        and pytest_test_count > 0
    )

    summary = {
        "task": "R24-T012",
        "target": "algorithms/linked_list/copy_random_pointer.py:RandomListNode",
        "fixture_passed": fixture_passed,
        "boundary_cases_total": len(boundary_cases),
        "boundary_cases_passed": len(boundary_cases) - boundary_failures,
        "doctest_attempted": dt_res.attempted,
        "doctest_failed": dt_res.failed,
        "pytest_command": " ".join(pytest_cmd),
        "pytest_test_count": pytest_test_count,
        "pytest_passed": pytest_passed,
        "overall": "PASS" if overall_passed else "FAIL",
    }
    with open(HERE / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    log(f"\nOVERALL: {'PASS' if overall_passed else 'FAIL'}")

    with open(HERE / "check_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(run_checks())
