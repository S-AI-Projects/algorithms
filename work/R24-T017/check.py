#!/usr/bin/env python3
"""Focused check runner for R24-T017: prims_minimum_spanning worked example.

Executes:
1. Source anchor: prims_minimum_spanning({1: [[1, 2]], 2: [[1, 1]]}) -> 1
2. Neighbor fixture: triangle graph -> 3
3. Intermediate state tracing (decisive greedy choice transition)
4. Doctest extraction and execution of prims_minimum_spanning docstring
5. Native pytest on tests/test_graph.py::TestPrimsWorkedExample
"""

from __future__ import annotations

import doctest
import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

pms_module = importlib.import_module("algorithms.graph.prims_minimum_spanning")
prims_minimum_spanning = pms_module.prims_minimum_spanning

WORK_DIR = PROJECT_ROOT / "work" / "R24-T017"
WORK_DIR.mkdir(parents=True, exist_ok=True)


def trace_prims(graph: dict) -> list[dict]:
    """Simulate and trace the intermediate states of prims_minimum_spanning."""
    import heapq

    vis: list = []
    heap: list = [[0, 1]]
    prim: set = set()
    mincost = 0
    steps = []

    step_num = 0
    while len(heap) > 0:
        step_num += 1
        cost, node = heapq.heappop(heap)
        skipped = node in vis
        pushed = []

        if not skipped:
            mincost += cost
            prim.add(node)
            vis.append(node)
            for distance, adjacent in graph[node]:
                if adjacent not in vis:
                    heapq.heappush(heap, [distance, adjacent])
                    pushed.append([distance, adjacent])

        steps.append(
            {
                "step": step_num,
                "popped": [cost, node],
                "skipped": skipped,
                "mincost_after": mincost,
                "vis_after": list(vis),
                "heap_remaining": [list(item) for item in heap],
                "pushed": pushed,
            }
        )
    return steps


def main() -> int:
    log_lines = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("R24-T017: prims_minimum_spanning Worked Example Verification")
    log("=" * 60)

    # 1. Source anchor check
    anchor_input = {1: [[1, 2]], 2: [[1, 1]]}
    expected_anchor_output = 1
    actual_anchor_output = prims_minimum_spanning(anchor_input)
    assert actual_anchor_output == expected_anchor_output, (
        f"Anchor expected {expected_anchor_output}, got {actual_anchor_output}"
    )
    log(f"PASS: Source anchor {anchor_input} -> {actual_anchor_output}")

    # 2. Neighbor check
    neighbor_input = {
        1: [[1, 2], [4, 3]],
        2: [[1, 1], [2, 3]],
        3: [[4, 1], [2, 2]],
    }
    expected_neighbor_output = 3
    actual_neighbor_output = prims_minimum_spanning(neighbor_input)
    assert actual_neighbor_output == expected_neighbor_output, (
        f"Neighbor expected {expected_neighbor_output}, got {actual_neighbor_output}"
    )
    log(f"PASS: Neighbor graph -> {actual_neighbor_output}")

    # 3. Intermediate trace & decisive transition check
    trace = trace_prims(neighbor_input)
    log(f"Traced {len(trace)} steps through neighbor graph execution.")
    # Check decisive step (step where weight 2 is picked over weight 4)
    # Step 1: pop [0, 1], push [1, 2], [4, 3]
    # Step 2: pop [1, 2], visit node 2, push [2, 3]
    # Step 3: heap has [2, 3] and [4, 3]. Pops [2, 3] (greedy choice!)
    decisive_step = trace[2]
    assert decisive_step["popped"] == [2, 3], (
        f"Unexpected decisive step: {decisive_step}"
    )
    log(
        f"PASS: Decisive greedy step verified: popped {decisive_step['popped']} "
        f"over edge [4, 3] with cumulative mincost={decisive_step['mincost_after']}"
    )

    # 4. Doctest check
    dt_result = doctest.testmod(pms_module, verbose=False)
    assert dt_result.failed == 0, f"Doctest failed: {dt_result}"
    assert dt_result.attempted >= 2, (
        f"Doctest attempted too few examples: {dt_result.attempted}"
    )
    log(
        f"PASS: Doctest verified {dt_result.attempted} examples"
        f" with {dt_result.failed} failures"
    )

    # 5. Native project test suite execution
    test_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "tests/test_graph.py::TestPrimsWorkedExample",
    ]
    log(f"Running focused native test: {' '.join(test_cmd)}")
    result = subprocess.run(
        test_cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    log(result.stdout)
    if result.stderr:
        log(result.stderr)
    assert result.returncode == 0, f"Focused test failed with code {result.returncode}"
    log("PASS: Native pytest suite passed.")

    # Write evidence artifacts
    inputs_data = {
        "source_anchor": {
            "graph": {str(k): v for k, v in anchor_input.items()},
            "expected": expected_anchor_output,
        },
        "neighbor": {
            "graph": {str(k): v for k, v in neighbor_input.items()},
            "expected": expected_neighbor_output,
        },
    }
    with open(WORK_DIR / "inputs.json", "w") as f:
        json.dump(inputs_data, f, indent=2)

    results_data = {
        "anchor_result": actual_anchor_output,
        "neighbor_result": actual_neighbor_output,
        "trace_step_count": len(trace),
        "decisive_step": decisive_step,
        "doctest": {
            "attempted": dt_result.attempted,
            "failed": dt_result.failed,
        },
        "pytest": {
            "returncode": result.returncode,
            "command": " ".join(test_cmd),
        },
    }
    with open(WORK_DIR / "results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    summary_data = {
        "task": "R24-T017",
        "status": "PASS",
        "function": "prims_minimum_spanning",
        "module": "algorithms.graph.prims_minimum_spanning",
        "source_anchor_passed": True,
        "neighbor_passed": True,
        "decisive_transition_verified": True,
        "doctest_passed": True,
        "pytest_passed": True,
    }
    with open(WORK_DIR / "summary.json", "w") as f:
        json.dump(summary_data, f, indent=2)

    def get_pkg_version(pkg: str) -> str:
        try:
            return importlib.metadata.version(pkg)
        except Exception:
            return "unknown"

    tool_versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "pytest": get_pkg_version("pytest"),
        "ruff": get_pkg_version("ruff"),
        "black": get_pkg_version("black"),
    }
    with open(WORK_DIR / "tool_versions.json", "w") as f:
        json.dump(tool_versions, f, indent=2)

    anchor_graph_str = json.dumps(inputs_data["source_anchor"]["graph"])
    worked_example_md = (
        "# Worked Example: Prim's Minimum Spanning Tree Algorithm\n\n"
        "## Function Under Test\n"
        "`algorithms.graph.prims_minimum_spanning.prims_minimum_spanning`\n\n"
        "## Problem Context\n"
        "Find the total weight of a Minimum Spanning Tree (MST) for a connected"
        " undirected graph.\n"
        "The algorithm starts from node `1` and greedily selects minimum weight"
        " frontier edges.\n\n"
        "## 1. Source Anchor Input\n"
        f"- Input: `{anchor_graph_str}`\n"
        "- Expected MST weight: `1`\n"
        "- Execution:\n"
        "  - Start node `1` with cost `0`.\n"
        "  - Edge `(1, 2)` of weight `1` is popped. Node `2` visited.\n"
        "  - Final MST weight: `1`.\n\n"
        "## 2. Neighboring Supported Input\n"
        "- Triangle graph nodes `1`, `2`, `3`:\n"
        "  - `1`: `[[1, 2], [4, 3]]`\n"
        "  - `2`: `[[1, 1], [2, 3]]`\n"
        "  - `3`: `[[4, 1], [2, 2]]`\n"
        "- Expected MST weight: `3`\n\n"
        "### Step-by-Step State Trace\n"
        "| Step | Action | Popped | Skipped | Weight | Visited |\n"
        "|---|---|---|---|---|---|\n"
        "| 1 | Visit node 1 | `[0, 1]` | No | 0 | `[1]` |\n"
        "| 2 | Visit node 2 | `[1, 2]` | No | 1 | `[1, 2]` |\n"
        "| 3 | **Decisive**: `[2,3]` beats `[4,3]` | `[2, 3]` | No | 3 | `[1,2,3]` |\n"
        "| 4 | Node 3 already visited | `[4, 3]` | Yes | 3 | `[1,2,3]` |\n\n"
        "### Decisive Transition\n"
        "Node `3` reachable via edge `(1,3)` weight `4` or `(2,3)` weight `2`.\n"
        "Prim's pops `[2, 3]` (cost 2 < 4) completing MST with weight `1+2=3`.\n\n"
        "## 3. Verification\n"
        "- Check: `python3 work/R24-T017/check.py`\n"
        "- Tests: `pytest -v tests/test_graph.py::TestPrimsWorkedExample`\n"
    )
    with open(WORK_DIR / "worked_example.md", "w") as f:
        f.write(worked_example_md)

    with open(WORK_DIR / "check_output.txt", "w") as f:
        f.write("\n".join(log_lines) + "\n")

    log("=" * 60)
    log("All checks completed successfully. Evidence generated in work/R24-T017/")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
