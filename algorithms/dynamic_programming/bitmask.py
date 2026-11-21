"""Bitmask dynamic programming — Travelling Salesman Problem (TSP).

Uses DP with bitmask to find the minimum-cost Hamiltonian cycle in a
weighted graph. The state (visited_mask, current_city) encodes which
cities have been visited and where we are now.

Complexity, with n = number of cities (rows of the distance matrix):
    Time:  O(2^n * n^2) worst case. Every reachable state (mask, pos) is
           solved once, there are (n - 1) * (2^(n-2) - 1) + 1 of them, and
           each scans all n cities, so the bound is tight: Theta(2^n * n^2).
    Space: O(2^n * n) for the memo table, plus recursion depth n.

    Observed (work/R24-T049 experiment, not a guarantee): the number of
    distance-matrix lookups equals the exact count predicted from those
    states for n = 1..14. It grows by 2.7x to 2.4x per extra city for
    n = 8..14, close to the 2 * ((n + 1) / n)^2 step of 2^n * n^2, and
    stays below 0.1 * 2^n * n^2.

Inspired by PR #855 (AmandaStromdahl).
"""

from __future__ import annotations

import math


def tsp(dist: list[list[float]]) -> float:
    """Return the minimum cost of a Hamiltonian cycle.

    *dist* is an n x n distance matrix; ``dist[i][j]`` is the cost of going
    from city i to city j. The tour starts and ends at city 0 and visits
    every other city exactly once. The matrix is only read, never changed,
    and the result keeps the numeric type of the entries (``int`` in, ``int``
    out). A single city gives ``dist[0][0]``; an empty matrix has no tour
    and gives ``math.inf``.

    >>> tsp([[0, 10, 15, 20],
    ...      [10, 0, 35, 25],
    ...      [15, 35, 0, 30],
    ...      [20, 25, 30, 0]])
    80
    >>> tsp([[0]])
    0
    >>> tsp([])
    inf
    """
    n = len(dist)
    full_mask = (1 << n) - 1
    dp: dict[tuple[int, int], float] = {}

    def solve(mask: int, pos: int) -> float:
        if mask == full_mask:
            return dist[pos][0]
        key = (mask, pos)
        if key in dp:
            return dp[key]
        ans = math.inf
        for city in range(n):
            if not (mask & (1 << city)):
                ans = min(ans, dist[pos][city] + solve(mask | (1 << city), city))
        dp[key] = ans
        return ans

    return solve(1, 0)
