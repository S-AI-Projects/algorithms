"""
Trimmed Mean

Compute the mean of an array after discarding a given percentage of the
highest and lowest values. Useful for robust averaging in scoring systems.

Reference: https://en.wikipedia.org/wiki/Truncated_mean

Complexity:
    Time:  O(n log n) due to sorting
    Space: O(n) for the trimmed copy
"""

from __future__ import annotations


def trimmean(array: list[float], percentage: float) -> float:
    """Calculate the trimmed mean of an array.

    Discards the top and bottom halves of the given percentage before
    computing the arithmetic mean.

    Contract & Worked Trace:
        - In-place mutation: `array` is sorted in-place.
        - Trimming ratio: `ratio = percentage / 200` yields the fraction discarded
          from each tail.
        - Decisive state transition: `trim_count = int(len(array) * ratio)`.
          Elements from index 0 to `trim_count - 1` (lowest) and from
          `len(array) - trim_count` upward (highest) are excluded.
          The remaining inner slice `trimmed` is averaged.

    Concrete Walkthrough:
        Given `array = [10.0, 2.0, 4.0, 8.0, 6.0]` and `percentage = 40`:
        1. In-place sort transitions array to: `[2.0, 4.0, 6.0, 8.0, 10.0]`.
        2. `ratio = 40 / 200 = 0.20`.
        3. `trim_count = int(5 * 0.20) = 1` element dropped from each end.
        4. Decisive slice: `array[1:4]` produces `[4.0, 6.0, 8.0]`.
        5. Final mean: `(4.0 + 6.0 + 8.0) / 3 = 18.0 / 3 = 6.0`.

    Args:
        array: List of numeric values.
        percentage: Total percentage to trim (split equally between
            top and bottom, 0 <= percentage < 100). E.g., 20 trims the top 10%
            and bottom 10%.

    Returns:
        The trimmed arithmetic mean.

    Examples:
        >>> trimmean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 20)
        5.5
        >>> trimmean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 40)
        5.5
        >>> trimmean([10.0, 2.0, 4.0, 8.0, 6.0], 40)
        6.0
        >>> trimmean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0)
        5.5
    """
    ratio = percentage / 200
    array.sort()
    trim_count = int(len(array) * ratio)
    trimmed = array[trim_count : len(array) - trim_count]
    total = 0
    for value in trimmed:
        total += value
    return total / len(trimmed)
