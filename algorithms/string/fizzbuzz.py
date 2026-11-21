"""
FizzBuzz

Return an array of numbers from 1 to N, replacing multiples of 3 with 'Fizz',
multiples of 5 with 'Buzz', and multiples of both with 'FizzBuzz'.

Reference: https://en.wikipedia.org/wiki/Fizz_buzz

Complexity:
    Time:  O(n)
    Space: O(n)
"""

from __future__ import annotations


def fizzbuzz(number: int) -> list[int | str]:
    """Generate FizzBuzz sequence from 1 to number.

    Args:
        number: The upper bound of the sequence (inclusive).

    Returns:
        A list where multiples of 3 are 'Fizz', multiples of 5 are 'Buzz',
        multiples of both are 'FizzBuzz', and all others are the integer value.

    Raises:
        ValueError: If number is less than 1.
        TypeError: If number is None.

    Failure paths:
        The guard ``if number < 1`` raises
        ``ValueError("n cannot be less than one")``. The smallest input that
        reaches it is ``0``; ``1`` is the smallest valid input and gives
        ``[1]``. ``None`` raises ``TypeError`` as documented, but from the
        ``number < 1`` comparison itself, so the later ``number is None``
        check is never reached. A failed call leaves nothing behind: no state
        is kept between calls and every successful call returns a new list.

    Examples:
        >>> fizzbuzz(5)
        [1, 2, 'Fizz', 4, 'Buzz']
        >>> fizzbuzz(0)
        Traceback (most recent call last):
            ...
        ValueError: n cannot be less than one
    """
    if number < 1:
        raise ValueError("n cannot be less than one")
    if number is None:
        raise TypeError("n cannot be None")

    result: list[int | str] = []
    for value in range(1, number + 1):
        if value % 3 == 0 and value % 5 == 0:
            result.append("FizzBuzz")
        elif value % 3 == 0:
            result.append("Fizz")
        elif value % 5 == 0:
            result.append("Buzz")
        else:
            result.append(value)
    return result


def fizzbuzz_with_helper_func(number: int) -> list[int | str]:
    """Generate FizzBuzz sequence using a helper function.

    Args:
        number: The upper bound of the sequence (inclusive).

    Returns:
        A list of FizzBuzz values from 1 to number. Unlike ``fizzbuzz``,
        there is no guard: any ``number`` below 1 gives the empty list.

    Examples:
        >>> fizzbuzz_with_helper_func(3)
        [1, 2, 'Fizz']
        >>> fizzbuzz_with_helper_func(0)
        []
    """
    return [_fb(value) for value in range(1, number + 1)]


def _fb(value: int) -> int | str:
    """Return the FizzBuzz value for a single number.

    Args:
        value: The number to evaluate.

    Returns:
        'Fizz', 'Buzz', 'FizzBuzz', or the number itself.
    """
    result = (value % 3 == 0) * "Fizz" + (value % 5 == 0) * "Buzz"
    return result if result != "" else value
