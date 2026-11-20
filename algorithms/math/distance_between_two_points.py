"""
Distance Between Two Points in 2D Space

Calculate the Euclidean distance between two points using the distance
formula derived from the Pythagorean theorem.

Reference: https://en.wikipedia.org/wiki/Euclidean_distance

Complexity:
    Time:  O(1)
    Space: O(1)
"""

from __future__ import annotations

from math import sqrt


def distance_between_two_points(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate the Euclidean distance between two points in 2D space.

    Args:
        x1: x-coordinate of the first point.
        y1: y-coordinate of the first point.
        x2: x-coordinate of the second point.
        y2: y-coordinate of the second point.

    Returns:
        The Euclidean distance between the two points.

    Contract:
        Returns ``sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)`` as a ``float``,
        even for ``int`` inputs. The result is never negative, is ``0.0``
        when the points are equal, and does not change if the two points are
        swapped or both are shifted by the same amount. The function is pure:
        it reads four numbers, has no side effects, and returns the same
        result for the same (or equal ``int``/``float``) inputs.

        For integer coordinates with ``dx ** 2 + dy ** 2 < 2 ** 53``, the sum
        is exact, so the result is the correctly rounded square root of that
        integer.

    Worked example:
        From ``(-1, -1)`` to ``(2, 3)``: ``dx = 2 - (-1) = 3`` and
        ``dy = 3 - (-1) = 4``, so the distance is ``sqrt(9 + 16) = sqrt(25)``,
        which is ``5.0``.

    Limits:
        Each difference is squared before the square root, so the result is
        reliable only while ``|dx|`` and ``|dy|`` are roughly between
        ``1e-154`` and ``1e154``. Larger differences raise ``OverflowError``
        (``distance_between_two_points(0, 0, 1e200, 0)``) and much smaller
        ones underflow to ``0.0`` (``distance_between_two_points(0, 0,
        1e-200, 0)``), although the true distances are ``1e200`` and
        ``1e-200``. ``math.hypot`` avoids both.

    Examples:
        >>> distance_between_two_points(0, 0, 3, 4)
        5.0
        >>> distance_between_two_points(-1, -1, 2, 3)
        5.0
        >>> distance_between_two_points(2, 3, 2, 3)
        0.0
    """
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
