"""
Integer Base Conversion

Convert integers between arbitrary bases (2-36). Supports conversion from
integer to string representation in a given base, and vice versa.

Reference: https://en.wikipedia.org/wiki/Positional_notation

Complexity:
    Time:  O(log_base(num)) for both directions
    Space: O(log_base(num))
"""

from __future__ import annotations

import string


def int_to_base(num: int, base: int) -> str:
    """Convert a base-10 integer to a string in the given base.

    Args:
        num: The integer to convert.
        base: The target base (2-36).

    Returns:
        String representation of num in the given base.

    Contract:
        Supported input is any ``int`` ``num`` and a ``base`` from 2 to 36.
        Digits are ``0-9`` then uppercase ``A-Z``, with no leading zeros;
        ``0`` gives ``"0"`` and a negative ``num`` gets a ``"-"`` prefix.
        Bases outside 2..36 are not supported: base 1 never terminates,
        base 0 raises ``ZeroDivisionError`` and bases above 36 can raise
        ``IndexError``.

    Determinism:
        The function is pure. Its only dependency is the constant digit
        alphabet ``string.digits + string.ascii_uppercase``. It does no I/O
        and does not use time, randomness, the environment, locale or any
        mutable global state, so the same ``(num, base)`` always gives the
        same string, in any order of calls and in a fresh interpreter.
        ``num`` is an immutable ``int``; ``num *= -1`` only rebinds the local
        name, so the caller's value is never changed.

    Examples:
        >>> int_to_base(5, 2)
        '101'
        >>> int_to_base(255, 16)
        'FF'
        >>> int_to_base(0, 2)
        '0'
        >>> int_to_base(-255, 16)
        '-FF'
    """
    is_negative = False
    if num == 0:
        return "0"
    if num < 0:
        is_negative = True
        num *= -1
    digit = string.digits + string.ascii_uppercase
    res = ""
    while num > 0:
        res += digit[num % base]
        num //= base
    if is_negative:
        return "-" + res[::-1]
    return res[::-1]


def base_to_int(str_to_convert: str, base: int) -> int:
    """Convert a string in a given base to a base-10 integer.

    Args:
        str_to_convert: The string representation of the number.
        base: The base of the input string (2-36).

    Returns:
        The base-10 integer value.

    Examples:
        >>> base_to_int('101', 2)
        5
        >>> base_to_int('FF', 16)
        255
    """
    digit = {}
    for ind, char in enumerate(string.digits + string.ascii_uppercase):
        digit[char] = ind
    multiplier = 1
    res = 0
    for char in str_to_convert[::-1]:
        res += digit[char] * multiplier
        multiplier *= base
    return res
