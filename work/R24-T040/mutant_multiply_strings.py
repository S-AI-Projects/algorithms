"""
Mutant of algorithms/string/multiply_strings.py for mutation testing.

Plausible one-line mistake:
Line 42: Altered accumulation condition from `accumulator += product` to `accumulator = product`.
This mimics an accidental assignment/overwrite in the inner loop rather than accumulation.
"""

from __future__ import annotations


def multiply(num1: str, num2: str) -> str:
    """Multiply two numbers represented as strings (MUTANT)."""
    intermediate: list[int] = []
    zero = ord("0")
    position_i = 1
    for digit_i in reversed(num1):
        position_j = 1
        accumulator = 0
        for digit_j in reversed(num2):
            product = (
                (ord(digit_i) - zero) * (ord(digit_j) - zero) * position_j * position_i
            )
            position_j *= 10
            accumulator = product  # MUTANT: accidental overwrite instead of accumulator += product
        position_i *= 10
        intermediate.append(accumulator)
    return str(sum(intermediate))

