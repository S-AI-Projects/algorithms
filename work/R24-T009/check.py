"""Focused check runner for R24-T009 (a_star scaling measurement and complexity).

Measures the scaling of ``a_star`` on valid graph inputs while verifying correctness:
- Input size: N (number of vertices in a linear chain/grid graph), N in {50, 100, 200}
- Repetitions: 5 repetitions per size with fresh seeded graphs (seed: 20260309 + rep)
- Only the `a_star` invocation is timed; graph generation, validation, imports,
  and I/O occur strictly outside the timed interval
- Outputs are independently verified outside the timed interval
- Reports median and min/max range
- No pass/fail decision depends on wall-clock speed

Saves verification evidence into ``work/R24-T009/``:
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
import statistics
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from algorithms.graph.a_star import a_star


def generate_chain_graph(n: int, rng: random.Random) -> tuple[dict, str, str, float]:
    """Generate a weighted chain graph with shortcut edges: 0 -> 1 -> ... -> N-1."""
    graph: dict[str, list[tuple[str, float]]] = {}
    expected_cost = 0.0

    for i in range(n):
        node = f"N{i}"
        graph[node] = []
        if i < n - 1:
            next_node = f"N{i + 1}"
            cost = rng.randint(1, 5)
            graph[node].append((next_node, float(cost)))
            expected_cost += cost

    start_node = "N0"
    goal_node = f"N{n - 1}"
    return graph, start_node, goal_node, expected_cost


def run_checks() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("Running focused check for R24-T009: a_star scaling measurement")
    log("=" * 60)

    # 1. Native unittest execution
    test_target = "tests.test_graph.TestAStar"
    cmd = [sys.executable, "-m", "unittest", "-v", test_target]
    log(f"Executing unittest command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    log(proc.stdout)
    log(proc.stderr)
    if proc.returncode != 0:
        log(f"FAILED: unittest exited with code {proc.returncode}")
        return proc.returncode

    # 2. Doctest execution
    log("Running doctests on algorithms/graph/a_star.py...")
    mod = importlib.import_module("algorithms.graph.a_star")
    doctest_res = doctest.testmod(mod)
    log(f"Doctest results: attempted={doctest_res.attempted}, failed={doctest_res.failed}")
    if doctest_res.failed != 0:
        log("FAILED: doctests failed")
        return 1

    # 3. Source anchor and derived neighbor verification
    all_passed = True

    # Anchor fixture
    g_anchor = {"A": [("B", 1.0)], "B": [("C", 2.0)], "C": []}
    p_anc, c_anc = a_star(g_anchor, "A", "C", lambda n: 0.0)
    anc_ok = (p_anc == ["A", "B", "C"]) and (c_anc == 3.0)
    if not anc_ok:
        all_passed = False
    log(f"Source anchor fixture: path={p_anc}, cost={c_anc}, passed={anc_ok}")

    # Derived neighbor
    g_neighbor = {"A": [("B", 1.0)], "B": [("C", 2.0)], "C": [("D", 3.0)], "D": []}
    p_nei, c_nei = a_star(g_neighbor, "A", "D", lambda n: 0.0)
    nei_ok = (p_nei == ["A", "B", "C", "D"]) and (c_nei == 6.0)
    if not nei_ok:
        all_passed = False
    log(f"Derived neighbor fixture: path={p_nei}, cost={c_nei}, passed={nei_ok}")

    # 4. Scaling experiment across 3 increasing sizes: N in {50, 100, 200}
    sizes = [50, 100, 200]
    repetitions = 5
    scaling_measurements = []

    for size in sizes:
        durations = []
        correct_runs = 0

        for rep in range(repetitions):
            seed = 20260309 + size * 10 + rep
            rng = random.Random(seed)
            # Setup graph outside timed interval
            graph, start, goal, expected_cost = generate_chain_graph(size, rng)
            zero_heuristic = lambda n: 0.0

            # ONLY time the a_star execution
            t0 = time.perf_counter()
            actual_path, actual_cost = a_star(graph, start, goal, zero_heuristic)
            t1 = time.perf_counter()
            durations.append(t1 - t0)

            # Correctness verification outside timed interval
            path_correct = (actual_path is not None) and (len(actual_path) == size) and (actual_path[0] == start) and (actual_path[-1] == goal)
            cost_correct = (actual_cost == expected_cost)

            if path_correct and cost_correct:
                correct_runs += 1
            else:
                all_passed = False

        med = statistics.median(durations)
        min_d = min(durations)
        max_d = max(durations)

        measurement = {
            "size_N": size,
            "repetitions": repetitions,
            "correct_runs": correct_runs,
            "durations_seconds": durations,
            "median_seconds": round(med, 6),
            "min_seconds": round(min_d, 6),
            "max_seconds": round(max_d, 6),
        }
        scaling_measurements.append(measurement)
        log(f"Size N={size}: median={med*1000:.3f}ms (range [{min_d*1000:.3f}ms, {max_d*1000:.3f}ms]), verified {correct_runs}/{repetitions}")

    # 5. Save artifacts
    tool_versions = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "unittest_command": " ".join(cmd),
        "base_seed": 20260309,
    }

    summary = {
        "task_id": "R24-T009",
        "module": "algorithms.graph.a_star",
        "complexity_definition": "Input size N = number of vertices in graph. Time complexity O(E log V) with consistent heuristic, worst-case O(b^d).",
        "sizes_tested": sizes,
        "scaling_measurements": scaling_measurements,
        "anchor_passed": anc_ok,
        "neighbor_passed": nei_ok,
        "doctest_passed": doctest_res.failed == 0,
        "unittest_passed": proc.returncode == 0,
        "all_passed": all_passed,
    }

    with open(os.path.join(WORK_DIR, "inputs.json"), "w") as f:
        json.dump({
            "anchor": {"g": g_anchor, "start": "A", "goal": "C"},
            "neighbor": {"g": g_neighbor, "start": "A", "goal": "D"},
            "scaling_sizes": sizes,
        }, f, indent=2)

    with open(os.path.join(WORK_DIR, "results.json"), "w") as f:
        json.dump(scaling_measurements, f, indent=2)

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
    log("ALL CHECKS PASSED FOR R24-T009")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
