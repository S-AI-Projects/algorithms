"""
Randomized Set

Design a data structure that supports insert, remove, and getRandom
in average O(1) time. Uses a list for random access and a dictionary
for O(1) lookup/removal.

Reference: https://leetcode.com/problems/insert-delete-getrandom-o1/

Complexity:
    Time:  O(1) average for insert, remove, get_random
    Space: O(n)
"""

from __future__ import annotations

import random


class RandomizedSet:
    """A set supporting O(1) insert, remove, and random element access.

    Contract & Repeatability:
        - Elements: Supports unique integers stored with O(1) average lookup,
          insertion, and removal.
        - Dependency seam: Supports an optional ``rng`` (an instance of
          ``random.Random``) in ``__init__`` for deterministic, repeatable testing.
          Defaults to ``None``, preserving compatibility by falling back to the
          global ``random`` module.
        - Isolation: Each instance maintains its own internal list and mapping;
          operations on one instance never affect another.

    Examples:
        >>> rs = RandomizedSet()
        >>> rs.insert(1)
        True
        >>> rs.insert(1)
        False
        >>> rs.insert(2)
        True
        >>> rs.remove(1)
        True
        >>> rs.get_random()
        2
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        """Initialize the randomized set.

        Args:
            rng: Optional random number generator for deterministic execution.
                Defaults to None (uses global random module).
        """
        self.nums: list[int] = []
        self.idxs: dict[int, int] = {}
        self._rng: random.Random | None = rng

    def insert(self, val: int) -> bool:
        """Insert a value into the set.

        Args:
            val: Value to insert.

        Returns:
            True if the value was inserted, False if already present.
        """
        if val not in self.idxs:
            self.nums.append(val)
            self.idxs[val] = len(self.nums) - 1
            return True
        return False

    def remove(self, val: int) -> bool:
        """Remove a value from the set.

        Args:
            val: Value to remove.

        Returns:
            True if the value was removed, False if not present.
        """
        if val in self.idxs:
            idx, last = self.idxs[val], self.nums[-1]
            self.nums[idx], self.idxs[last] = last, idx
            self.nums.pop()
            self.idxs.pop(val, 0)
            return True
        return False

    def get_random(self) -> int:
        """Return a random element from the set.

        Returns:
            A randomly chosen element.
        """
        if not self.nums:
            raise IndexError("Cannot get random element from an empty RandomizedSet")
        if self._rng is not None:
            idx = self._rng.randint(0, len(self.nums) - 1)
        else:
            idx = random.randint(0, len(self.nums) - 1)
        return self.nums[idx]
