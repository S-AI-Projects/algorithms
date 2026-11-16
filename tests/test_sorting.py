import unittest

from algorithms.sorting import (
    Interval,
    bitonic_sort,
    bogo_sort,
    bubble_sort,
    bucket_sort,
    can_attend_meetings,
    cocktail_shaker_sort,
    comb_sort,
    counting_sort,
    cycle_sort,
    exchange_sort,
    gnome_sort,
    insertion_sort,
    max_heap_sort,
    merge_sort,
    min_heap_sort,
    pancake_sort,
    pigeonhole_sort,
    quick_sort,
    radix_sort,
    selection_sort,
    shell_sort,
)


def is_sorted(array):
    """
    Helper function to check if the given array is sorted.
    :param array: Array to check if sorted
    :return: True if sorted in ascending order, else False
    """
    return all(array[i] <= array[i + 1] for i in range(len(array) - 1))


class TestSuite(unittest.TestCase):
    def test_bogo_sort(self):
        self.assertTrue(is_sorted(bogo_sort([1, 23, 5])))

    def test_bitonic_sort(self):
        self.assertTrue(is_sorted(bitonic_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_bubble_sort(self):
        self.assertTrue(is_sorted(bubble_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_comb_sort(self):
        self.assertTrue(is_sorted(comb_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_counting_sort(self):
        self.assertTrue(is_sorted(counting_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_cycle_sort(self):
        self.assertTrue(is_sorted(cycle_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_exchange_sort(self):
        self.assertTrue(is_sorted(exchange_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_heap_sort(self):
        self.assertTrue(is_sorted(max_heap_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

        self.assertTrue(is_sorted(min_heap_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_insertion_sort(self):
        self.assertTrue(is_sorted(insertion_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_merge_sort(self):
        self.assertTrue(is_sorted(merge_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_pancake_sort(self):
        self.assertTrue(is_sorted(pancake_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_pigeonhole_sort(self):
        self.assertTrue(is_sorted(pigeonhole_sort([1, 5, 65, 23, 57, 1232])))

    def test_quick_sort(self):
        self.assertTrue(is_sorted(quick_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_selection_sort(self):
        self.assertTrue(is_sorted(selection_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_bucket_sort(self):
        self.assertTrue(is_sorted(bucket_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_shell_sort(self):
        self.assertTrue(is_sorted(shell_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_radix_sort(self):
        self.assertTrue(is_sorted(radix_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_gnome_sort(self):
        self.assertTrue(is_sorted(gnome_sort([1, 3, 2, 5, 65, 23, 57, 1232])))

    def test_cocktail_shaker_sort(self):
        self.assertTrue(is_sorted(cocktail_shaker_sort([1, 3, 2, 5, 65, 23, 57, 1232])))


def _reference_can_attend(intervals: list[Interval]) -> bool:
    """Independent O(n^2) pairwise reference oracle without sorting."""
    n = len(intervals)
    for i in range(n):
        for j in range(i + 1, n):
            if max(intervals[i].start, intervals[j].start) < min(intervals[i].end, intervals[j].end):
                return False
    return True


class TestMeetingRooms(unittest.TestCase):
    def test_meeting_rooms_fixtures(self):
        # Anchor fixture [3, 1, 2]: start times permuted, non-overlapping
        self.assertTrue(
            can_attend_meetings([Interval(3, 4), Interval(1, 2), Interval(2, 3)])
        )
        # Already ordered [1, 2, 3]
        self.assertTrue(
            can_attend_meetings([Interval(1, 2), Interval(2, 3), Interval(3, 4)])
        )
        # Reversed [3, 2, 1]
        self.assertTrue(
            can_attend_meetings([Interval(3, 4), Interval(2, 3), Interval(1, 2)])
        )
        # Multiplicities [2, 2, 1]: repeated start time creates overlap
        self.assertFalse(
            can_attend_meetings([Interval(2, 3), Interval(2, 4), Interval(1, 2)])
        )
        # Smallest supported collections
        self.assertTrue(can_attend_meetings([]))
        self.assertTrue(can_attend_meetings([Interval(1, 5)]))

        # Distinct LeetCode examples
        self.assertFalse(
            can_attend_meetings([Interval(0, 30), Interval(5, 10), Interval(15, 20)])
        )
        self.assertTrue(can_attend_meetings([Interval(7, 10), Interval(2, 4)]))

    def test_meeting_rooms_oracle_cross_check(self):
        test_inputs = [
            [],
            [Interval(1, 2)],
            [Interval(1, 2), Interval(2, 3)],
            [Interval(1, 3), Interval(2, 4)],
            [Interval(0, 5), Interval(5, 10), Interval(10, 15)],
            [Interval(0, 10), Interval(2, 3), Interval(11, 12)],
            [Interval(10, 20), Interval(0, 5), Interval(5, 10)],
            [Interval(1, 10), Interval(2, 5)],
            [Interval(1, 2), Interval(3, 4), Interval(5, 6), Interval(7, 8)],
            [Interval(7, 8), Interval(5, 6), Interval(3, 4), Interval(1, 2)],
            [Interval(1, 4), Interval(2, 3), Interval(5, 6)],
            [Interval(2, 6), Interval(8, 10), Interval(15, 18)],
            [Interval(1, 5), Interval(5, 6), Interval(6, 7), Interval(7, 8)],
            [Interval(1, 5), Interval(4, 6)],
            [Interval(0, 1), Interval(1, 2), Interval(2, 3), Interval(3, 4)],
            [Interval(0, 2), Interval(1, 3)],
            [Interval(5, 10), Interval(0, 5), Interval(10, 15)],
            [Interval(10, 15), Interval(5, 10), Interval(0, 5)],
            [Interval(3, 5), Interval(1, 2), Interval(6, 8)],
            [Interval(1, 100), Interval(50, 60)],
            [Interval(2, 3), Interval(3, 4), Interval(4, 5), Interval(5, 6)],
        ]
        self.assertGreaterEqual(len(test_inputs), 20)
        for intervals in test_inputs:
            actual = can_attend_meetings(intervals)
            expected = _reference_can_attend(intervals)
            self.assertEqual(
                actual,
                expected,
                f"Mismatch for input {intervals}: got {actual}, expected {expected}",
            )

    def test_meeting_rooms_does_not_mutate_input(self):
        intervals = [Interval(3, 4), Interval(1, 2), Interval(2, 3)]
        snapshot = [(iv.start, iv.end) for iv in intervals]
        result = can_attend_meetings(intervals)
        self.assertTrue(result)
        current = [(iv.start, iv.end) for iv in intervals]
        self.assertEqual(current, snapshot)


if __name__ == "__main__":
    unittest.main()
