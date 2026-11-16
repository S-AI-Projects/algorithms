"""Focused check runner for R24-T004 (Node invariants and is_cyclic properties).

Verifies invariants of ``Node`` and ``is_cyclic`` in
``algorithms/linked_list/is_cyclic.py``:
- A->B->C three-node fixture with values and links verified separately
- Smallest supported collections: None, single node, self-loop
- Deterministic property test generating 100 pseudo-random bounded list topologies (seed 20260309)
- Negative path verification: ensures invariant verification catches deliberately corrupted links

Saves verification evidence into ``work/R24-T004/``:
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
import random
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from algorithms.linked_list.is_cyclic import Node, is_cyclic


def verify_acyclic_invariant(head: Node | None, expected_values: list) -> tuple[bool, str]:
    """Verify that traversal terminates, encounters expected nodes once, and preserves links."""
    visited_nodes: list[Node] = []
    curr = head
    while curr is not None:
        if curr in visited_nodes:
            return False, "Cycle detected in supposedly acyclic list"
        visited_nodes.append(curr)
        curr = curr.next

    actual_values = [n.val for n in visited_nodes]
    if actual_values != expected_values:
        return False, f"Values mismatch: got {actual_values}, expected {expected_values}"

    # Verify link chain integrity
    for i in range(len(visited_nodes) - 1):
        if visited_nodes[i].next is not visited_nodes[i + 1]:
            return False, f"Broken link between index {i} and {i + 1}"
    if visited_nodes and visited_nodes[-1].next is not None:
        return False, "Terminal node does not point to None"

    return True, "Invariant holds"


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T004: Node invariant and is_cyclic")
    log("=" * 60)

    # 1. Native unittest execution
    test_targets = [
        "tests.test_linked_list.TestSuite.test_node_invariants_and_fixtures",
        "tests.test_linked_list.TestSuite.test_node_property_generator_100_cases",
        "tests.test_linked_list.TestSuite.test_is_cyclic",
    ]
    cmd = [sys.executable, "-m", "unittest", "-v"] + test_targets
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/linked_list/is_cyclic.py...")
    mod = importlib.import_module("algorithms.linked_list.is_cyclic")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Direct fixture verification
    fixtures_results = []
    all_passed = True

    # Fixture: A -> B -> C
    a, b, c = Node("A"), Node("B"), Node("C")
    a.next, b.next, c.next = b, c, None
    ok, reason = verify_acyclic_invariant(a, ["A", "B", "C"])
    cyc_result = is_cyclic(a)
    passed = ok and (cyc_result is False)
    if not passed:
        all_passed = False
    fixtures_results.append({
        "id": "fixture_A_B_C",
        "description": "Three distinct nodes A -> B -> C",
        "expected_cyclic": False,
        "actual_cyclic": cyc_result,
        "invariant_valid": ok,
        "passed": passed,
    })
    log(f"Fixture A->B->C: passed={passed} ({reason})")

    # Smallest list: None
    ok_none, reason_none = verify_acyclic_invariant(None, [])
    cyc_none = is_cyclic(None)
    passed_none = ok_none and (cyc_none is False)
    if not passed_none:
        all_passed = False
    fixtures_results.append({
        "id": "smallest_list_none",
        "description": "Empty list (None)",
        "expected_cyclic": False,
        "actual_cyclic": cyc_none,
        "invariant_valid": ok_none,
        "passed": passed_none,
    })

    # Single node: Node(1)
    single = Node(1)
    ok_single, _ = verify_acyclic_invariant(single, [1])
    cyc_single = is_cyclic(single)
    passed_single = ok_single and (cyc_single is False)
    if not passed_single:
        all_passed = False
    fixtures_results.append({
        "id": "single_node",
        "description": "Single isolated node Node(1)",
        "expected_cyclic": False,
        "actual_cyclic": cyc_single,
        "invariant_valid": ok_single,
        "passed": passed_single,
    })

    # Self-loop: single.next = single
    single.next = single
    cyc_self = is_cyclic(single)
    passed_self = (cyc_self is True)
    if not passed_self:
        all_passed = False
    fixtures_results.append({
        "id": "single_self_loop",
        "description": "Single node with self-loop",
        "expected_cyclic": True,
        "actual_cyclic": cyc_self,
        "invariant_valid": True,
        "passed": passed_self,
    })

    # 4. Property-based generator: 100 bounded valid cases (seed 20260309)
    rng = random.Random(20260309)
    generator_cases = []
    generator_passed = 0

    for i in range(100):
        length = rng.randint(1, 20)
        nodes = [Node(f"v{k}") for k in range(length)]
        for k in range(length - 1):
            nodes[k].next = nodes[k + 1]

        has_cycle = rng.choice([True, False])
        cycle_entry = None
        if has_cycle:
            cycle_entry = rng.randint(0, length - 1)
            nodes[-1].next = nodes[cycle_entry]

        # Snapshot pointers and values
        val_snapshot = [n.val for n in nodes]
        next_snapshot = [n.next for n in nodes]

        head = nodes[0]
        actual_cycle = is_cyclic(head)

        # Invariant checks
        mutation_detected = ([n.val for n in nodes] != val_snapshot) or ([n.next for n in nodes] != next_snapshot)
        correct_result = (actual_cycle == has_cycle)
        case_passed = correct_result and not mutation_detected

        if case_passed:
            generator_passed += 1
        else:
            all_passed = False

        generator_cases.append({
            "case_id": i,
            "length": length,
            "has_cycle": has_cycle,
            "cycle_entry": cycle_entry,
            "actual_cycle": actual_cycle,
            "passed": case_passed,
        })

    log(f"Property generator (100 bounded cases): {generator_passed}/100 passed")

    # 5. Negative path verification (deliberately broken invariant check)
    corrupted_a, corrupted_b, corrupted_c = Node("A"), Node("B"), Node("C")
    corrupted_a.next = corrupted_c  # Deliberately broken: skips B
    corrupted_c.next = None
    neg_ok, neg_reason = verify_acyclic_invariant(corrupted_a, ["A", "B", "C"])
    negative_path_verified = (neg_ok is False)  # Must detect failure
    if not negative_path_verified:
        all_passed = False
        log("FAILED: Negative path check failed to detect broken link")
    else:
        log(f"Negative path check verified: correctly rejected corrupted link ({neg_reason})")

    # 6. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
        "seed": 20260309,
    }

    summary = {
        "task_id": "R24-T004",
        "module": "algorithms.linked_list.is_cyclic",
        "fixtures_checked": len(fixtures_results),
        "fixtures_passed": sum(1 for f in fixtures_results if f["passed"]),
        "generator_cases_total": len(generator_cases),
        "generator_cases_passed": generator_passed,
        "negative_path_verified": negative_path_verified,
        "doctest_passed": doctest_res.failed == 0,
        "unittest_passed": proc.returncode == 0,
        "all_passed": all_passed,
    }

    with open(os.path.join(WORK_DIR, "inputs.json"), "w") as f:
        json.dump({
            "fixtures": fixtures_results,
            "generator_sample": generator_cases[:10],
        }, f, indent=2)

    with open(os.path.join(WORK_DIR, "results.json"), "w") as f:
        json.dump({
            "fixtures_results": fixtures_results,
            "generator_results": generator_cases,
            "negative_path_detected": not neg_ok,
        }, f, indent=2)

    with open(os.path.join(WORK_DIR, "tool_versions.json"), "w") as f:
        json.dump(tool_versions, f, indent=2)

    with open(os.path.join(WORK_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    with open(os.path.join(WORK_DIR, "check_output.txt"), "w") as f:
        f.write("\n".join(log_lines) + "\n")

    if not all_passed:
        log("FAILED: One or more checks failed.")
        return 1

    log("=" * 60)
    log("ALL CHECKS PASSED FOR R24-T004")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
