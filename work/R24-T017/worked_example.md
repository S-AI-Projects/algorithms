# Worked Example: Prim's Minimum Spanning Tree Algorithm

## Function Under Test
`algorithms.graph.prims_minimum_spanning.prims_minimum_spanning`

## Problem Context
Find the total weight of a Minimum Spanning Tree (MST) for a connected undirected graph.
The algorithm starts from node `1` and greedily selects minimum weight frontier edges.

## 1. Source Anchor Input
- Input: `{"1": [[1, 2]], "2": [[1, 1]]}`
- Expected MST weight: `1`
- Execution:
  - Start node `1` with cost `0`.
  - Edge `(1, 2)` of weight `1` is popped. Node `2` visited.
  - Final MST weight: `1`.

## 2. Neighboring Supported Input
- Triangle graph nodes `1`, `2`, `3`:
  - `1`: `[[1, 2], [4, 3]]`
  - `2`: `[[1, 1], [2, 3]]`
  - `3`: `[[4, 1], [2, 2]]`
- Expected MST weight: `3`

### Step-by-Step State Trace
| Step | Action | Popped | Skipped | Weight | Visited |
|---|---|---|---|---|---|
| 1 | Visit node 1 | `[0, 1]` | No | 0 | `[1]` |
| 2 | Visit node 2 | `[1, 2]` | No | 1 | `[1, 2]` |
| 3 | **Decisive**: `[2,3]` beats `[4,3]` | `[2, 3]` | No | 3 | `[1,2,3]` |
| 4 | Node 3 already visited | `[4, 3]` | Yes | 3 | `[1,2,3]` |

### Decisive Transition
Node `3` reachable via edge `(1,3)` weight `4` or `(2,3)` weight `2`.
Prim's pops `[2, 3]` (cost 2 < 4) completing MST with weight `1+2=3`.

## 3. Verification
- Check: `python3 work/R24-T017/check.py`
- Tests: `pytest -v tests/test_graph.py::TestPrimsWorkedExample`
