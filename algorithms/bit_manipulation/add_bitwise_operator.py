"""
Add Bitwise Operator

Add two positive integers without using the '+' operator, using only
bitwise operations (AND, XOR, shift).

Reference: https://en.wikipedia.org/wiki/Adder_(electronics)

Complexity:
    Time:  O(log n) where n is the larger of the two inputs
    Space: O(1)
"""

from __future__ import annotations


def add_bitwise_operator(first: int, second: int) -> int:
    """Add two non-negative integers using only bitwise operations.

    Algorithm:
        Uses XOR to compute the sum-without-carry and AND + left-shift to
        propagate the carry.  The loop terminates because the carry is shifted
        left each iteration, eventually becoming 0.

    Protected invariant (mutation-resistant):
        ``add_bitwise_operator(a, b) == a + b`` for all non-negative a, b.
        A one-line mutation that replaces ``carry = first & second`` with
        ``carry = first | second`` causes the wrong carry, breaking the
        invariant on inputs like (2, 3): mutant produces 6 instead of 5.

    Args:
        first: First non-negative integer operand.
        second: Second non-negative integer operand.

    Returns:
        The sum of first and second.

    Raises:
        ValueError: If either operand is negative.

    Examples:
        >>> add_bitwise_operator(2, 3)
        5
        >>> add_bitwise_operator(0, 0)
        0
        >>> add_bitwise_operator(1, 1)
        2
    """
    if first < 0 or second < 0:
        raise ValueError("The provided values must be non-negative!")
    while second:
        carry = first & second
        first = first ^ second
        second = carry << 1
    return first
