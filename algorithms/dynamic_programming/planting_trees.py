"""
Planting Trees

Given an even number of trees along one side of a road, calculate the
minimum total distance to move them into valid positions on both sides
at even intervals.

Reference: https://en.wikipedia.org/wiki/Dynamic_programming

Complexity:
    Time:  O(n^2)
    Space: O(n^2)
"""

from __future__ import annotations

from math import sqrt


def planting_trees(trees: list[int], length: int, width: int) -> float:
    """Compute the minimum distance to rearrange trees to valid positions.

    Contract & Supported Boundaries:
        - Pure function: does not mutate the input trees list.
        - Supported tree domain: Requires an even number of trees N >= 4 (at least 2 pairs),
          as spacing between pairs is length / (n_pairs - 1) where n_pairs = len(trees) // 2.
        - Road boundaries: length >= 0 and width >= 0.
        - At length == 0, all target locations collapse to 0.0.
        - At width == 0, cross-road displacement penalties are 0.0.

    Args:
        trees: Sorted list of current tree positions along the road (even length >= 4).
        length: Length of the road (>= 0).
        width: Width of the road (>= 0).

    Returns:
        Minimum total distance the trees must be moved.

    Examples:
        >>> planting_trees([0, 1, 10, 10], 10, 1)
        2.414213562373095
        >>> planting_trees([0, 0, 10, 10], 10, 1)
        2.0
        >>> planting_trees([0, 0, 10, 10], 10, 0)
        0.0
        >>> planting_trees([0, 0, 0, 0], 0, 0)
        0.0
    """
    trees = [0] + trees

    n_pairs = int(len(trees) / 2)

    space_between_pairs = length / (n_pairs - 1)

    target_locations = [location * space_between_pairs for location in range(n_pairs)]

    cmatrix = [[0 for _ in range(n_pairs + 1)] for _ in range(n_pairs + 1)]
    for r_i in range(1, n_pairs + 1):
        cmatrix[r_i][0] = cmatrix[r_i - 1][0] + sqrt(
            width + abs(trees[r_i] - target_locations[r_i - 1]) ** 2
        )
    for l_i in range(1, n_pairs + 1):
        cmatrix[0][l_i] = cmatrix[0][l_i - 1] + abs(
            trees[l_i] - target_locations[l_i - 1]
        )

    for r_i in range(1, n_pairs + 1):
        for l_i in range(1, n_pairs + 1):
            cmatrix[r_i][l_i] = min(
                cmatrix[r_i - 1][l_i]
                + sqrt(width + (trees[l_i + r_i] - target_locations[r_i - 1]) ** 2),
                cmatrix[r_i][l_i - 1]
                + abs(trees[l_i + r_i] - target_locations[l_i - 1]),
            )

    return cmatrix[n_pairs][n_pairs]
