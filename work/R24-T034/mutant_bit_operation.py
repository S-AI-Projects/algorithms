"""
Mutant of algorithms/bit_manipulation/bit_operation.py for invariant testing.

Deliberately breaks the invariant in get_bit:
Line 36: Inverted condition `(number & (1 << position)) == 0` instead of `!= 0`.
"""

from __future__ import annotations


def get_bit(number: int, position: int) -> int:
    """Get the bit value at a specific position (MUTANT)."""
    # Invariant broken: returns 1 when bit is 0, and 0 when bit is 1
    return (number & (1 << position)) == 0


def set_bit(number: int, position: int) -> int:
    return number | (1 << position)


def clear_bit(number: int, position: int) -> int:
    mask = ~(1 << position)
    return number & mask


def update_bit(number: int, position: int, bit: int) -> int:
    mask = ~(1 << position)
    return (number & mask) | (bit << position)
