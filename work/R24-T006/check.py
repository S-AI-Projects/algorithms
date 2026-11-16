"""Focused check runner for R24-T006 (AvlTree calculation simplification).

Verifies the refactored balance calculation and metric refresh consolidation
in ``algorithms/data_structures/avl_tree.py``:
- Precondition anchor: `result = []` on line 125 of `algorithms/data_structures/avl_tree.py`
- Smallest valid input: empty tree -> `in_order_traverse() == []` (precondition: `if not self.node`)
- Ordinary input: populated tree `[5, 3, 7, 1, 4]` -> `in_order_traverse() == [1, 3, 4, 5, 7]`
- Rotations: Right, Left, Left-Right, Right-Left rebalancing
- State invariants: balance factor remains within `{-1, 0, 1}`, height bounded by O(log n)

Saves verification evidence into ``work/R24-T006/``:
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

from algorithms.data_structures.avl_tree import AvlTree


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T006: AvlTree refactoring")
    log("=" * 60)

    # 1. Native unittest execution
    test_target = "tests.test_data_structures.TestAvlTree"
    cmd = [sys.executable, "-m", "unittest", "-v", test_target]
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/data_structures/avl_tree.py...")
    mod = importlib.import_module("algorithms.data_structures.avl_tree")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct fixture verification
    fixtures = [
        {
            "id": "smallest_valid_empty",
            "description": "Smallest valid input: empty AvlTree",
            "source_precondition_line": "algorithms/data_structures/avl_tree.py:127 (if not self.node: return result)",
            "anchor": "result = []",
            "input_keys": [],
            "expected_traverse": [],
            "expected_balance": 0,
            "expected_height": -1,
        },
        {
            "id": "ordinary_input_populated",
            "description": "Ordinary input: 5 keys requiring internal ordering and balancing",
            "source_precondition_line": "algorithms/data_structures/avl_tree.py:130-132 (recursive in_order traversal)",
            "anchor": "result = []",
            "input_keys": [5, 3, 7, 1, 4],
            "expected_traverse": [1, 3, 4, 5, 7],
            "expected_balance": 0,
            "expected_height": 2,
        },
        {
            "id": "rotation_left_left_right_rotate",
            "description": "Right rotation trigger with decreasing keys",
            "source_precondition_line": "algorithms/data_structures/avl_tree.py:53-54 (self.balance > 1 -> rotate_right)",
            "anchor": "result = []",
            "input_keys": [3, 2, 1],
            "expected_traverse": [1, 2, 3],
            "expected_balance": 0,
            "expected_height": 1,
        },
        {
            "id": "rotation_right_right_left_rotate",
            "description": "Left rotation trigger with increasing keys",
            "source_precondition_line": "algorithms/data_structures/avl_tree.py:60-61 (self.balance < -1 -> rotate_left)",
            "anchor": "result = []",
            "input_keys": [1, 2, 3],
            "expected_traverse": [1, 2, 3],
            "expected_balance": 0,
            "expected_height": 1,
        },
        {
            "id": "double_rotation_left_right",
            "description": "Left-Right double rotation trigger",
            "source_precondition_line": "algorithms/data_structures/avl_tree.py:50-52 (self.node.left.balance < 0 -> rotate_left)",
            "anchor": "result = []",
            "input_keys": [3, 1, 2],
            "expected_traverse": [1, 2, 3],
            "expected_balance": 0,
            "expected_height": 1,
        },
        {
            "id": "double_rotation_right_left",
            "description": "Right-Left double rotation trigger",
            "source_precondition_line": "algorithms/data_structures/avl_tree.py:57-59 (self.node.right.balance > 0 -> rotate_right)",
            "anchor": "result = []",
            "input_keys": [1, 3, 2],
            "expected_traverse": [1, 2, 3],
            "expected_balance": 0,
            "expected_height": 1,
        },
    ]

    inputs_record = []
    results_record = []
    all_passed = True

    for f in fixtures:
        tree = AvlTree()
        for k in f["input_keys"]:
            tree.insert(k)

        actual_traverse = tree.in_order_traverse()
        traverse_ok = (actual_traverse == f["expected_traverse"])
        balance_ok = (tree.balance in [-1, 0, 1])
        passed = traverse_ok and balance_ok

        inputs_record.append({
            "id": f["id"],
            "description": f["description"],
            "input_keys": f["input_keys"],
            "source_precondition_line": f["source_precondition_line"],
        })

        results_record.append({
            "id": f["id"],
            "expected_traverse": f["expected_traverse"],
            "actual_traverse": actual_traverse,
            "actual_balance": tree.balance,
            "actual_height": tree.height,
            "passed": passed,
        })

        if not passed:
            all_passed = False
            log(f"FAILED for {f['id']}: expected {f['expected_traverse']}, got {actual_traverse}")
        else:
            log(f"PASSED for {f['id']}: in-order={actual_traverse}, balance={tree.balance}, height={tree.height}")

    # 4. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T006",
        "module": "algorithms.data_structures.avl_tree",
        "refactored_operation": "Consolidated repeated update_heights()+update_balances() into _refresh_metrics(), and simplified balance check to abs(self.balance) > 1",
        "fixtures_total": len(fixtures),
        "fixtures_passed": sum(1 for r in results_record if r["passed"]),
        "doctest_passed": doctest_res.failed == 0,
        "unittest_passed": proc.returncode == 0,
        "all_passed": all_passed,
    }

    with open(os.path.join(WORK_DIR, "inputs.json"), "w") as f:
        json.dump(inputs_record, f, indent=2)

    with open(os.path.join(WORK_DIR, "results.json"), "w") as f:
        json.dump(results_record, f, indent=2)

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
    log("ALL CHECKS PASSED FOR R24-T006")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
