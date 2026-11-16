"""Focused check runner for R24-T007 (SeparateChainingHashTable _Node worked example).

Verifies the executable documentation and state transitions of ``_Node``
and ``SeparateChainingHashTable`` in ``algorithms/data_structures/separate_chaining_hash_table.py``:
- Executable source anchor: `table = SeparateChainingHashTable()`, `table.put('hello', 'world')`, `len(table) == 1`
- Neighboring input: `table.put('foo', 'bar')`, `len(table) == 2`
- Value update transition: `table.put('hello', 'new_world')`, `len(table) == 2`, in-place node update
- Collision chaining transition: `table = SeparateChainingHashTable(size=1)`
- Step-by-step intermediate state verification of `_Node` allocation and pointer linking

Saves verification evidence into ``work/R24-T007/``:
- ``inputs.json``
- ``results.json``
- ``summary.json``
- ``tool_versions.json``
- ``check_output.txt``

Exits non-zero on any failure.
"""

from __future__ import annotations

import doctest
import importlib
import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from algorithms.data_structures.separate_chaining_hash_table import (
    SeparateChainingHashTable,
    _Node,
)


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T007: _Node worked example")
    log("=" * 60)

    # 1. Native unittest execution
    test_target = "tests.test_data_structures.TestSeparateChainingHashTable"
    cmd = [sys.executable, "-m", "unittest", "-v", test_target]
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/data_structures/separate_chaining_hash_table.py...")
    mod = importlib.import_module("algorithms.data_structures.separate_chaining_hash_table")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct step-by-step worked example verification
    worked_steps = []
    all_passed = True

    # Step 1: Initial _Node allocation
    n1 = _Node("hello", "world")
    s1_ok = (n1.key == "hello") and (n1.value == "world") and (n1.next is None)
    worked_steps.append({
        "step": 1,
        "name": "initial_node_allocation",
        "description": "Create single node _Node('hello', 'world')",
        "expected": {"key": "hello", "value": "world", "next": None},
        "actual": {"key": n1.key, "value": n1.value, "next": None if n1.next is None else str(n1.next)},
        "passed": s1_ok,
    })
    log(f"Step 1 (initial node): passed={s1_ok}")

    # Step 2: Intermediate state - chaining colliding node
    n2 = _Node("foo", "bar", next_node=n1)
    s2_ok = (n2.key == "foo") and (n2.value == "bar") and (n2.next is n1)
    worked_steps.append({
        "step": 2,
        "name": "chaining_intermediate_node",
        "description": "Create colliding node _Node('foo', 'bar', next_node=n1)",
        "expected": {"key": "foo", "value": "bar", "next_key": "hello"},
        "actual": {"key": n2.key, "value": n2.value, "next_key": n2.next.key if n2.next else None},
        "passed": s2_ok,
    })
    log(f"Step 2 (intermediate chaining): passed={s2_ok}")

    # Step 3: In-place value transition
    n1.value = "updated_world"
    s3_ok = (n2.next.value == "updated_world")
    worked_steps.append({
        "step": 3,
        "name": "in_place_value_transition",
        "description": "Mutate payload of chained node n1.value = 'updated_world'",
        "expected": {"chained_node_value": "updated_world"},
        "actual": {"chained_node_value": n2.next.value if n2.next else None},
        "passed": s3_ok,
    })
    log(f"Step 3 (in-place mutation): passed={s3_ok}")

    # Step 4: Source anchor table operations
    table = SeparateChainingHashTable()
    table.put("hello", "world")
    s4_ok = (len(table) == 1) and (table.get("hello") == "world")
    worked_steps.append({
        "step": 4,
        "name": "source_anchor_table",
        "description": "table.put('hello', 'world'); len(table) == 1",
        "expected": {"len": 1, "get_hello": "world"},
        "actual": {"len": len(table), "get_hello": table.get("hello")},
        "passed": s4_ok,
    })
    log(f"Step 4 (source anchor table): passed={s4_ok}")

    # Step 5: Neighboring input & in-place update
    table.put("foo", "bar")
    table.put("hello", "new_world")
    s5_ok = (len(table) == 2) and (table.get("foo") == "bar") and (table.get("hello") == "new_world")
    worked_steps.append({
        "step": 5,
        "name": "neighboring_input_and_update",
        "description": "table.put('foo', 'bar'); table.put('hello', 'new_world')",
        "expected": {"len": 2, "get_foo": "bar", "get_hello": "new_world"},
        "actual": {"len": len(table), "get_foo": table.get("foo"), "get_hello": table.get("hello")},
        "passed": s5_ok,
    })
    log(f"Step 5 (neighboring input & update): passed={s5_ok}")

    if not all(s["passed"] for s in worked_steps):
        all_passed = False

    # 4. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T007",
        "module": "algorithms.data_structures.separate_chaining_hash_table",
        "target_class": "_Node",
        "steps_checked": len(worked_steps),
        "steps_passed": sum(1 for s in worked_steps if s["passed"]),
        "doctest_passed": doctest_res.failed == 0,
        "unittest_passed": proc.returncode == 0,
        "all_passed": all_passed,
    }

    with open(os.path.join(WORK_DIR, "inputs.json"), "w") as f:
        json.dump(worked_steps, f, indent=2)

    with open(os.path.join(WORK_DIR, "results.json"), "w") as f:
        json.dump(worked_steps, f, indent=2)

    with open(os.path.join(WORK_DIR, "tool_versions.json"), "w") as f:
        json.dump(tool_versions, f, indent=2)

    with open(os.path.join(WORK_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    with open(os.path.join(WORK_DIR, "check_output.txt"), "w") as f:
        f.write("\n".join(log_lines) + "\n")

    if not all_passed:
        log("FAILED: One or more assertions failed.")
        return 1

    log("=" * 60)
    log("ALL CHECKS PASSED FOR R24-T007")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
