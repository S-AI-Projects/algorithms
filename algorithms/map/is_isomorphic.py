"""
Isomorphic Strings

Determine if two strings are isomorphic. Two strings are isomorphic if
characters in s can be mapped to characters in t while preserving order,
with a one-to-one mapping.

Reference: https://leetcode.com/problems/isomorphic-strings/description/

Complexity:
    Time:  O(n) where n = len(s) = len(t); exactly one pass over character
           positions, with O(1) amortised dict/set operations per step.
    Space: O(k) where k is the number of distinct characters (at most 128
           for ASCII, so effectively O(1) in the alphabet-bounded case).

Operation count note:
    For equal-length inputs the loop executes exactly n iterations.
    Each iteration performs at most two hash-table look-ups and one
    hash-table insertion, so total operations scale linearly with n.
"""

from __future__ import annotations


def is_isomorphic(s: str, t: str) -> bool:
    """Check if two strings are isomorphic.

    Complexity: O(n) time, O(k) space where n = len(s) and k is the number
    of distinct characters in s (bounded by the alphabet size).

    Args:
        s: Source string.
        t: Target string.

    Returns:
        True if s and t are isomorphic, False otherwise.

    Examples:
        >>> is_isomorphic("egg", "add")
        True
        >>> is_isomorphic("foo", "bar")
        False
        >>> is_isomorphic("ab", "aa")
        False
    """
    if len(s) != len(t):
        return False
    mapping: dict[str, str] = {}
    mapped_values: set[str] = set()
    for i in range(len(s)):
        if s[i] not in mapping:
            if t[i] in mapped_values:
                return False
            mapping[s[i]] = t[i]
            mapped_values.add(t[i])
        else:
            if mapping[s[i]] != t[i]:
                return False
    return True

