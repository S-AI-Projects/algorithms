"""
Delete Reoccurring Characters

Given a string, delete any reoccurring characters and return the new string
containing only the first occurrence of each character.

Reference: https://en.wikipedia.org/wiki/Duplicate_removal

Complexity:
    Time:  O(n) where n is the length of the string
    Space: O(n)
"""

from __future__ import annotations


def delete_reoccurring_characters(string: str) -> str:
    """Remove duplicate characters, keeping only the first occurrence of each.

    Contract:
        - Input: any ``str``, including the empty string.
        - Output: a ``str`` holding each distinct character of ``string``
          exactly once, in the order of its first occurrence. Repeats are
          removed wherever they appear, not only when adjacent.
        - Characters are compared exactly, so the comparison is case-sensitive
          (``"aA"`` is returned unchanged).
        - ``""`` returns ``""``; a string with no repeats is returned unchanged.
        - Pure function: the argument is not modified and no state is kept
          between calls.

    Args:
        string: The input string to process.

    Returns:
        A new string with duplicate characters removed.

    Examples:
        >>> delete_reoccurring_characters("aaabcccc")
        'abc'
        >>> delete_reoccurring_characters("aaabcccca")
        'abc'
        >>> delete_reoccurring_characters("")
        ''
    """
    seen_characters: set[str] = set()
    output_string = ""
    for char in string:
        if char not in seen_characters:
            seen_characters.add(char)
            output_string += char
    return output_string
