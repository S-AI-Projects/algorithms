import random
import unittest

from algorithms.sorting import (
    bitonic_sort,
    bogo_sort,
    bubble_sort,
    bucket_sort,
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
    wiggle_sort,
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


class TestQuickSortFailureBehavior(unittest.TestCase):
    """Cover the failure / boundary behaviour of quick_sort (R24-T018).

    quick_sort sorts in-place and returns the same list object.
    The 'failure path' is the early-exit inside _quick_sort_recursive
    when first >= last (empty or single-element input).
    """

    def test_empty_list_smallest_collection(self):
        # Smallest supported collection: empty list -> [] (no-op, early exit)
        arr: list[int] = []
        result = quick_sort(arr)
        self.assertEqual(result, [])
        self.assertIs(result, arr)  # same object returned

    def test_single_element(self):
        arr = [42]
        result = quick_sort(arr)
        self.assertEqual(result, [42])
        self.assertIs(result, arr)

    def test_fixture_three_one_two(self):
        arr = [3, 1, 2]
        result = quick_sort(arr)
        self.assertEqual(result, [1, 2, 3])
        self.assertIs(result, arr)  # in-place: returns same object

    def test_fixture_duplicates(self):
        arr = [2, 2, 1]
        result = quick_sort(arr)
        self.assertEqual(result, [1, 2, 2])

    def test_already_ordered(self):
        arr = [1, 2, 3]
        result = quick_sort(arr)
        self.assertEqual(result, [1, 2, 3])

    def test_reversed_order(self):
        arr = [3, 2, 1]
        result = quick_sort(arr)
        self.assertEqual(result, [1, 2, 3])

    def test_in_place_mutation(self):
        # Document: the original list is mutated by the call
        original = [5, 3, 8, 1]
        saved_id = id(original)
        quick_sort(original)
        self.assertEqual(id(original), saved_id)
        self.assertEqual(original, [1, 3, 5, 8])

    def test_valid_call_after_empty_no_op(self):
        # An ordinary valid call succeeds after the no-op failure case
        empty: list[int] = []
        quick_sort(empty)  # no-op; must not corrupt internal state
        normal = [3, 1, 2]
        result = quick_sort(normal)
        self.assertEqual(result, [1, 2, 3])

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


class TestWiggleSortInvariant(unittest.TestCase):
    """Property and invariant test suite for wiggle_sort."""

    @staticmethod
    def is_wiggle_sorted(array: list[int]) -> bool:
        for i in range(len(array) - 1):
            if i % 2 == 0 and not (array[i] <= array[i + 1]):
                return False
            if i % 2 == 1 and not (array[i] >= array[i + 1]):
                return False
        return True

    def test_fixture_cases(self):
        # Fixture cases from brief: [3, 1, 2], [2, 2, 1],
        # ordered [1, 2, 3], reversed [3, 2, 1], smallest [] and [1]
        fixtures = [
            ([3, 1, 2], [1, 3, 2]),
            ([2, 2, 1], [1, 2, 2]),
            ([1, 2, 3], [1, 3, 2]),
            ([3, 2, 1], [1, 3, 2]),
            ([], []),
            ([1], [1]),
            ([1, 2], [1, 2]),
        ]
        for inp, expected in fixtures:
            with self.subTest(inp=inp):
                target = list(inp)
                res = wiggle_sort(target)
                self.assertIs(res, target)
                self.assertEqual(res, expected)
                self.assertTrue(self.is_wiggle_sorted(res))
                self.assertEqual(sorted(res), sorted(inp))

    def test_invariant_property_random_cases(self):
        # 100+ bounded valid cases with fixed seed
        rng = random.Random(24014)
        for _ in range(120):
            length = rng.randint(0, 30)
            arr = [rng.randint(-100, 100) for _ in range(length)]
            orig = list(arr)
            res = wiggle_sort(arr)
            self.assertIs(res, arr)
            self.assertEqual(sorted(res), sorted(orig))
            self.assertTrue(self.is_wiggle_sorted(res))


if __name__ == "__main__":
    unittest.main()
