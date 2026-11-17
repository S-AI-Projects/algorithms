"""
Contain String (strStr)

Return the index of the first occurrence of needle in haystack, or -1 if
needle is not part of haystack.

Reference: https://leetcode.com/problems/implement-strstr/

Complexity:
    Time:  O(n * m) worst case, where n = len(haystack), m = len(needle)
    Space: O(1)
"""

from __future__ import annotations


def contain_string(haystack: str, needle: str) -> int:
    """Find the first occurrence of needle in haystack.

    Input/Output Contract:
        - Input:
            - `haystack` (str): The string to search within.
            - `needle` (str): The substring to search for.
            Neither input string is mutated by the function.
        - Output:
            - Integer representing the 0-based index of the first occurrence
              of `needle` in `haystack`.
            - Returns -1 if `needle` is not found in `haystack`.
            - Returns 0 if `needle` is an empty string (""), including when
              `haystack` is also empty ("").
        - Preconditions / Invariants:
            - Comparison is exact and case-sensitive.
            - When multiple occurrences exist, only the earliest valid start
              index is returned.
            - Pure function: no external state is read or modified, and no state
              persists across calls.

    Args:
        haystack: The string to search in.
        needle: The string to search for.

    Returns:
        The index of the first occurrence, or -1 if not found.

    Examples:
        >>> contain_string("hello", "ll")
        2
        >>> contain_string("hello", "lo")
        3
        >>> contain_string("hello", "world")
        -1
        >>> contain_string("", "")
        0
    """
    if len(needle) == 0:
        return 0
    if len(needle) > len(haystack):
        return -1
    for index in range(len(haystack)):
        if len(haystack) - index < len(needle):
            return -1
        if haystack[index : index + len(needle)] == needle:
            return index
    return -1
