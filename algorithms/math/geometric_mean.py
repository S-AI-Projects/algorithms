"""Geometric mean — the nth root of the product of n numbers.

The geometric mean is useful for data that grows exponentially
(like investment returns, population growth, etc.) and for
finding the central tendency when dealing with ratios or rates.

Formula: GM = (x₁ × x₂ × ... × xₙ)^(1/n)
"""

from __future__ import annotations

import math


def geometric_mean(numbers: list[float]) -> float:
    """Return the geometric mean of a list of numbers.

    The geometric mean is the nth root of the product of n numbers.
    All numbers must be positive.

    Args:
        numbers: A list of positive numbers

    Returns:
        The geometric mean as a float

    Raises:
        ValueError: If the list is empty, has fewer than 1 element,
                   or contains non-positive numbers

    >>> round(geometric_mean([1, 2, 3, 4, 5]), 4)
    2.6052
    >>> round(geometric_mean([2, 8]), 4)
    4.0
    >>> round(geometric_mean([1, 1, 1]), 4)
    1.0
    >>> round(geometric_mean([100, 100, 100]), 4)
    100.0

    Worked example (input, intermediate state, result):

    The loop only builds a running product, so for ``[2, 8, 4]`` the state
    goes 1.0 -> 2.0 -> 16.0 -> 64.0. The decisive step is the return line,
    which turns that product into its n-th root. Here n = 3, so it computes
    ``64.0 ** (1 / 3)``, the cube root of 64, which is 4 because
    4 * 4 * 4 = 64. Floating-point roots can be off in the last digits, so
    the examples round to 4 places.

    >>> import math
    >>> from algorithms.math import geometric_mean
    >>> numbers = [2, 8, 4]
    >>> product = math.prod(numbers, start=1.0)  # the state the loop ends with
    >>> product
    64.0
    >>> round(product ** (1 / len(numbers)), 4)  # the n-th root, n = 3
    4.0
    >>> round(geometric_mean(numbers), 4)
    4.0
    """
    if not numbers:
        msg = "List cannot be empty"
        raise ValueError(msg)

    if any(num <= 0 for num in numbers):
        msg = "All numbers must be positive"
        raise ValueError(msg)

    n = len(numbers)
    product = 1.0
    for num in numbers:
        product *= num

    return product ** (1 / n)


def geometric_mean_logarithm(numbers: list[float]) -> float:
    """Return the geometric mean using logarithms (more numerically stable).

    This method avoids overflow/underflow for very large or very small numbers
    by using the property: GM = exp((ln(x₁) + ln(x₂) + ... + ln(xₙ)) / n)

    Args:
        numbers: A list of positive numbers

    Returns:
        The geometric mean as a float

    Raises:
        ValueError: If the list is empty or contains non-positive numbers

    >>> round(geometric_mean_logarithm([2, 8]), 4)
    4.0
    >>> round(geometric_mean_logarithm([1, 2, 3, 4, 5]), 4)
    2.6052
    """
    if not numbers:
        msg = "List cannot be empty"
        raise ValueError(msg)

    if any(num <= 0 for num in numbers):
        msg = "All numbers must be positive"
        raise ValueError(msg)

    log_sum = sum(math.log(num) for num in numbers)
    return math.exp(log_sum / len(numbers))
