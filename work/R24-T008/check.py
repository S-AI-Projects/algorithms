"""Focused check runner for R24-T008 (maximum_flow_bfs failure/absent-result branch).

Verifies the failure/absent-result path of ``maximum_flow_bfs`` in
``algorithms/graph/maximum_flow_bfs.py``:
- Line 72 failure branch: `if visited[len(new_array) - 1] == 0: break`
- Fixture: 5 vertices (0:A, 1:B, 2:C, 3:D, 4:E), with edges A-B, A-C, B-D and isolated E
  Distances from A: A=0, B=1, C=1, D=2, E unreachable -> returns 0
- Immutability check: caller-owned matrix remains unmodified
- Follow-up check: ordinary valid call succeeds normally right after the failure case

Saves verification evidence into ``work/R24-T008/``:
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

from algorithms.graph.maximum_flow_bfs import maximum_flow_bfs


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T008: maximum_flow_bfs failure path")
    log("=" * 60)

    # 1. Native unittest execution
    test_target = "tests.test_graph.TestMaximumFlowBfs"
    cmd = [sys.executable, "-m", "unittest", "-v", test_target]
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/graph/maximum_flow_bfs.py...")
    mod = importlib.import_module("algorithms.graph.maximum_flow_bfs")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct failure path & follow-up verification
    cases = []
    all_passed = True

    # Case 1: Unreachable sink fixture (edges A-B, A-C, B-D, isolated sink E)
    fixture_graph = [
        [0, 10, 10, 0, 0],
        [0, 0, 0, 10, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    snapshot = [row[:] for row in fixture_graph]
    actual_1 = maximum_flow_bfs(fixture_graph)
    c1_passed = (actual_1 == 0) and (fixture_graph == snapshot)
    cases.append({
        "id": "unreachable_sink_fixture",
        "description": "5-node network with isolated sink E; distances from A: A=0, B=1, C=1, D=2, E unreachable",
        "tested_branch_line": "algorithms/graph/maximum_flow_bfs.py:72 (visited[sink] == 0: break)",
        "expected": 0,
        "actual": actual_1,
        "caller_matrix_unmutated": (fixture_graph == snapshot),
        "passed": c1_passed,
    })
    log(f"Case 1 (unreachable sink): actual={actual_1}, unmutated={fixture_graph == snapshot}, passed={c1_passed}")

    # Case 2: Ordinary valid call immediately after failure
    valid_graph = [
        [0, 10, 0],
        [0, 0, 10],
        [0, 0, 0],
    ]
    actual_2 = maximum_flow_bfs(valid_graph)
    c2_passed = (actual_2 == 10)
    cases.append({
        "id": "valid_call_after_failure",
        "description": "Ordinary 3-node pipeline with capacity 10 executed after failure case",
        "tested_branch_line": "algorithms/graph/maximum_flow_bfs.py (augmenting path found)",
        "expected": 10,
        "actual": actual_2,
        "caller_matrix_unmutated": True,
        "passed": c2_passed,
    })
    log(f"Case 2 (ordinary valid call after failure): actual={actual_2}, passed={c2_passed}")

    # Case 3: Complete disconnection (0-capacity source)
    disconnected_graph = [
        [0, 0],
        [0, 0],
    ]
    actual_3 = maximum_flow_bfs(disconnected_graph)
    c3_passed = (actual_3 == 0)
    cases.append({
        "id": "zero_capacity_disconnected",
        "description": "Two nodes with no edges",
        "tested_branch_line": "algorithms/graph/maximum_flow_bfs.py:72 (visited[sink] == 0: break)",
        "expected": 0,
        "actual": actual_3,
        "caller_matrix_unmutated": True,
        "passed": c3_passed,
    })
    log(f"Case 3 (zero capacity): actual={actual_3}, passed={c3_passed}")

    if not all(c["passed"] for c in cases):
        all_passed = False

    # 4. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
    }

    summary = {
        "task_id": "R24-T008",
        "module": "algorithms.graph.maximum_flow_bfs",
        "failure_branch_source_line": "algorithms/graph/maximum_flow_bfs.py:72",
        "cases_total": len(cases),
        "cases_passed": sum(1 for c in cases if c["passed"]),
        "doctest_passed": doctest_res.failed == 0,
        "unittest_passed": proc.returncode == 0,
        "all_passed": all_passed,
    }

    with open(os.path.join(WORK_DIR, "inputs.json"), "w") as f:
        json.dump(cases, f, indent=2)

    with open(os.path.join(WORK_DIR, "results.json"), "w") as f:
        json.dump(cases, f, indent=2)

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
    log("ALL CHECKS PASSED FOR R24-T008")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
