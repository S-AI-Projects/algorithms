"""
Topological Sort (Kahn's Algorithm / BFS)

Computes a topological ordering of a directed acyclic graph.  Raises
ValueError when a cycle is detected.

Reference: https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm

Complexity:
    Time:  O(V + E)
    Space: O(V + E)
"""

from __future__ import annotations

from collections import defaultdict, deque


def topological_sort(vertices: int, edges: list[tuple[int, int]]) -> list[int]:
    """Return a topological ordering of the vertices.

    Args:
        vertices: Number of vertices (labelled 0 .. vertices-1).
        edges: Directed edges as (u, v) meaning u -> v.

    Returns:
        List of vertices in topological order.

    Raises:
        ValueError: If the graph contains a cycle (including a self-loop).

    Contract:
        Returns a new list containing every vertex ``0 .. vertices - 1``
        exactly once, with ``u`` before ``v`` for every edge ``(u, v)``.
        ``edges`` is only read. Among vertices that are ready at the same
        time, the order is first-in first-out, starting from the vertices
        with no incoming edges in increasing label order, so the result is
        deterministic. ``vertices=0`` gives ``[]``.

    Protected condition:
        ``in_degree[v]`` counts every edge into ``v``, including repeated
        edges, and ``v`` is queued only when that count drops to exactly 0,
        i.e. after all of its incoming edges have been processed. Counting
        an edge once fewer or more, or queuing ``v`` early, either places
        ``v`` before one of its predecessors or makes a valid graph look
        cyclic.

    Examples:
        >>> topological_sort(3, [(0, 1), (1, 2)])
        [0, 1, 2]
        >>> topological_sort(2, [(0, 1), (0, 1)])
        [0, 1]
        >>> topological_sort(3, [(0, 2), (0, 1), (1, 2)])
        [0, 1, 2]
    """
    graph: dict[int, list[int]] = defaultdict(list)

    in_degree = [0] * vertices

    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue: deque[int] = deque()
    for i in range(vertices):
        if in_degree[i] == 0:
            queue.append(i)

    sorted_order: list[int] = []
    processed = 0

    while queue:
        node = queue.popleft()
        sorted_order.append(node)
        processed += 1

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if processed != vertices:
        raise ValueError("Cycle detected, topological sort failed")

    return sorted_order
