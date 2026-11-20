"""
Prim's Minimum Spanning Tree

Computes the weight of a minimum spanning tree for a connected weighted
undirected graph using a priority queue.

Reference: https://en.wikipedia.org/wiki/Prim%27s_algorithm

Complexity:
    Time:  O(E log V)
    Space: O(V + E)
"""

from __future__ import annotations

import heapq
from typing import Any


def prims_minimum_spanning(
    graph_used: dict[Any, list[list[int | Any]]],
) -> int:
    """Return the total weight of the MST using Prim's algorithm.

    Contract:
        - Input: `graph_used`, an adjacency dictionary mapping each node to a list
          of `[weight, neighbor]` pairs for an undirected weighted connected graph.
          Node `1` is the designated start node.
        - Output: An integer representing the total sum of edge weights in the
          minimum spanning tree.
        - Non-mutation: `graph_used` is read-only and never modified.

    Worked Example:
        Given triangle graph with nodes 1, 2, 3:
        >>> g = {1: [[1, 2], [4, 3]], 2: [[1, 1], [2, 3]], 3: [[4, 1], [2, 2]]}
        >>> prims_minimum_spanning(g)
        3

        Step-by-step state trace:
        1. Initial state: `heap = [[0, 1]]`, `vis = []`, `mincost = 0`.
        2. Pop `[0, 1]`: visit node 1. `mincost = 0`.
           Adjacent edges pushed to heap: `[1, 2]` and `[4, 3]`.
        3. Pop `[1, 2]`: visit node 2. `mincost` becomes `0 + 1 = 1`.
           Adjacent edge pushed: `[2, 3]` (edge `[1, 1]` skipped as 1 is visited).
        4. Decisive transition: Heap contains `[2, 3]` and `[4, 3]`.
           Prim's greedy selection pops the lighter edge `[2, 3]` (weight 2)
           rather than direct edge `[4, 3]` (weight 4). Node 3 is visited.
           `mincost` becomes `1 + 2 = 3`.
        5. Pop `[4, 3]`: node 3 is already in `vis`, skipped.
        6. Heap is exhausted; returns total MST weight 3.

    Args:
        graph_used: Adjacency list as ``{node: [[weight, neighbour], ...]}``.

    Returns:
        Sum of edge weights in the minimum spanning tree.

    Examples:
        >>> prims_minimum_spanning({1: [[1, 2]], 2: [[1, 1]]})
        1
        >>> g = {1: [[1, 2], [4, 3]], 2: [[1, 1], [2, 3]], 3: [[4, 1], [2, 2]]}
        >>> prims_minimum_spanning(g)
        3
    """
    vis: list[Any] = []
    heap: list[list[int | Any]] = [[0, 1]]
    prim: set[Any] = set()
    mincost = 0

    while len(heap) > 0:
        cost, node = heapq.heappop(heap)
        if node in vis:
            continue

        mincost += cost
        prim.add(node)
        vis.append(node)

        for distance, adjacent in graph_used[node]:
            if adjacent not in vis:
                heapq.heappush(heap, [distance, adjacent])

    return mincost
