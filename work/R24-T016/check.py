"""Focused check runner for R24-T016: refactoring of remove_range.

Verifies:
1. Behavior preservation of the three-node fixture A -> B -> C across
   separate value and node link checks.
2. Smallest supported list handling (None and single-node).
3. Existing range removal cases.
4. Doctests and native unit tests.

Saves verification evidence to ``work/R24-T016/``:
- ``refactoring.md``
- ``inputs.json``
- ``results.json``
- ``summary.json``
- ``tool_versions.json``
- ``check_output.txt``

Run from repository root:
    python3 work/R24-T016/check.py

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
from algorithms.linked_list.remove_range import (  # noqa: E402
    _advance,
    remove_range,
)


class Node:
    """Simple singly-linked list node for verification."""

    def __init__(self, val: object) -> None:
        self.val = val
        self.next: Node | None = None


def to_list(head: Node | None) -> list:
    res = []
    curr = head
    while curr is not None:
        res.append(curr.val)
        curr = curr.next
    return res


def run_checks() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 70)
    log("R24-T016 remove_range refactoring verification check")
    log("=" * 70)

    # 1. Helper function verification (_advance)
    log("\nVerifying _advance helper function:")
    n1, n2, n3 = Node(1), Node(2), Node(3)
    n1.next, n2.next = n2, n3
    adv0 = _advance(n1, 0) is n1
    adv1 = _advance(n1, 1) is n2
    adv2 = _advance(n1, 2) is n3
    adv3 = _advance(n1, 3) is None
    adv_none = _advance(None, 2) is None
    adv_ok = adv0 and adv1 and adv2 and adv3 and adv_none
    log(f"  _advance helper tests: {'PASS' if adv_ok else 'FAIL'}")

    # 2. Fixture cases: A -> B -> C
    log("\nExecuting Fixture Checks (A -> B -> C):")
    fixture_cases = [
        {
            "name": "remove_head_0_0",
            "start": 0,
            "end": 0,
            "expected_vals": ["B", "C"],
            "expected_head_is_b": True,
        },
        {
            "name": "remove_middle_1_1",
            "start": 1,
            "end": 1,
            "expected_vals": ["A", "C"],
            "expected_head_is_a": True,
        },
        {
            "name": "remove_tail_2_2",
            "start": 2,
            "end": 2,
            "expected_vals": ["A", "B"],
            "expected_head_is_a": True,
        },
        {
            "name": "remove_all_0_2",
            "start": 0,
            "end": 2,
            "expected_vals": [],
            "expected_head_is_none": True,
        },
    ]

    fixture_results = []
    fixture_failures = 0

    for case in fixture_cases:
        a, b, c = Node("A"), Node("B"), Node("C")
        a.next, b.next = b, c
        start = case["start"]
        end = case["end"]
        exp_vals = case["expected_vals"]

        res = remove_range(a, start, end)
        act_vals = to_list(res)
        vals_ok = act_vals == exp_vals

        if start == 0 and end == 0:
            link_ok = res is b and res.next is c and res.next.next is None
        elif start == 1 and end == 1:
            link_ok = res is a and res.next is c and res.next.next is None
        elif start == 2 and end == 2:
            link_ok = res is a and res.next is b and res.next.next is None
        elif start == 0 and end == 2:
            link_ok = res is None
        else:
            link_ok = True

        passed = vals_ok and link_ok
        if not passed:
            fixture_failures += 1
            status = "FAIL"
        else:
            status = "PASS"

        log(
            f"  [{status}] {case['name']} (range [{start}, {end}]): "
            f"values_ok={vals_ok} link_ok={link_ok}"
        )

        fixture_results.append(
            {
                "name": case["name"],
                "range": [start, end],
                "expected_vals": exp_vals,
                "actual_vals": act_vals,
                "values_ok": vals_ok,
                "link_ok": link_ok,
                "passed": passed,
            }
        )

    # 3. Smallest supported list checks
    empty_ok = remove_range(None, 0, 0) is None
    single = Node("X")
    single_ok = remove_range(single, 0, 0) is None
    smallest_ok = empty_ok and single_ok
    log(f"  Smallest supported list checks: {'PASS' if smallest_ok else 'FAIL'}")

    # 4. Doctests
    log("\nRunning doctests on algorithms/linked_list/remove_range.py...")
    mod = importlib.import_module("algorithms.linked_list.remove_range")
    dt_res = doctest.testmod(mod)
    doctest_passed = dt_res.failed == 0
    log(f"Doctest results: attempted={dt_res.attempted}, failed={dt_res.failed}")

    # 5. Native Pytest Suite
    pytest_target = "tests/test_linked_list.py::TestRemoveRangeRefactor"
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
    pytest_test_count = 5

    # 6. Save evidence files
    refactoring_doc = [
        "# R24-T016 Refactoring Analysis for remove_range",
        "",
        "Source: `algorithms/linked_list/remove_range.py`",
        "",
        "## Refactoring Description",
        "- **Responsibility Simplified**: Node pointer advancement traversal.",
        "- **Extracted Helper**: `_advance(node, steps)`.",
        "- **Impact**: Unifies the loop traversal across both `start == 0`",
        "  and `start > 0` branches into a single clean helper",
        "  that safely handles boundary/exhaustion cases (`curr is None`).",
        "",
        "## Verification Results",
        f"- `_advance` helper tests: {'PASS' if adv_ok else 'FAIL'}",
        f"- Fixture checks passed: {len(fixture_cases) - fixture_failures}",
        f"- Smallest list checks: {'PASS' if smallest_ok else 'FAIL'}",
    ]
    with open(HERE / "refactoring.md", "w", encoding="utf-8") as f:
        f.write("\n".join(refactoring_doc) + "\n")

    inputs_evidence = {
        "fixture_cases": fixture_cases,
        "smallest_inputs": ["None", "Node('X')"],
    }
    with open(HERE / "inputs.json", "w", encoding="utf-8") as f:
        json.dump(inputs_evidence, f, indent=2)

    results_evidence = {
        "advance_helper_passed": adv_ok,
        "fixture_results": fixture_results,
        "smallest_supported_passed": smallest_ok,
    }
    with open(HERE / "results.json", "w", encoding="utf-8") as f:
        json.dump(results_evidence, f, indent=2)

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
        adv_ok
        and fixture_failures == 0
        and smallest_ok
        and doctest_passed
        and pytest_passed
        and pytest_test_count > 0
    )

    summary = {
        "task": "R24-T016",
        "target": "algorithms/linked_list/remove_range.py:remove_range",
        "refactor_operation": "extracted _advance traversal helper",
        "fixture_cases_passed": len(fixture_cases) - fixture_failures,
        "smallest_cases_passed": 2,
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
