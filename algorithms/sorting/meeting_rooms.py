"""
Meeting Rooms

Given an array of meeting time intervals consisting of start and end times
[[s1, e1], [s2, e2], ...] (si < ei), determine if a person could attend
all meetings (i.e. no two meetings overlap).

Reference: https://leetcode.com/problems/meeting-rooms/

Complexity:
    Time:  O(n log n) best / O(n log n) average / O(n log n) worst
    Space: O(1)
"""

from __future__ import annotations


class Interval:
    """Represents a meeting time interval [start, end).

    Args:
        start: Start time of the meeting.
        end: End time of the meeting.
    """

    def __init__(self, start: int = 0, end: int = 0) -> None:
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"Interval({self.start}, {self.end})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Interval):
            return False
        return self.start == other.start and self.end == other.end


def can_attend_meetings(intervals: list[Interval]) -> bool:
    """Determine whether all meetings can be attended without overlap.

    Two meetings overlap if one meeting starts strictly before the previous
    meeting ends (i.e. intervals[i].start < intervals[i - 1].end).
    Consecutive meetings that touch at endpoints (e.g. [1, 2] and [2, 3])
    do not conflict and can both be attended.

    Args:
        intervals: List of interval objects with *start* and *end* attributes.

    Returns:
        True if a person can attend all meetings, False otherwise.

    Examples:
        >>> intervals = [Interval(0, 30), Interval(5, 10), Interval(15, 20)]
        >>> can_attend_meetings(intervals)
        False
        >>> intervals = [Interval(7, 10), Interval(2, 4)]
        >>> can_attend_meetings(intervals)
        True
        >>> intervals = [Interval(1, 2), Interval(2, 3)]
        >>> can_attend_meetings(intervals)
        True
    """
    intervals = sorted(intervals, key=lambda x: x.start)
    for i in range(1, len(intervals)):
        if intervals[i].start < intervals[i - 1].end:
            return False
    return True
