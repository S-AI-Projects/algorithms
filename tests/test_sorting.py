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


class TestBogoSortWorkedExample(unittest.TestCase):
    """Executable worked-example regression tests for bogo_sort (R24-T037).

    bogo_sort mutates *and* returns the same list object.
    The decisive state transition: ``_is_sorted`` returns True and
    the while-loop exits.  Every shuffle before that is an intermediate
    state that is discarded.

    random.shuffle is seeded before each call so the examples are
    deterministic and their displayed output can be asserted.
    """

    def setUp(self):
        import random
        random.seed(0)

    # ------------------------------------------------------------------
    # Fixture inputs — explicit expected values, ascending interface
    # ------------------------------------------------------------------

    def test_fixture_3_1_2(self):
        """[3, 1, 2] → [1, 2, 3]  (fixture anchor, seed 0)."""
        import random; random.seed(0)
        from algorithms.sorting.bogo_sort import bogo_sort
        result = bogo_sort([3, 1, 2])
        self.assertEqual(result, [1, 2, 3])

    def test_fixture_2_2_1(self):
        """[2, 2, 1] → [1, 2, 2]  (duplicates preserved, seed 0)."""
        import random; random.seed(0)
        from algorithms.sorting.bogo_sort import bogo_sort
        result = bogo_sort([2, 2, 1])
        self.assertEqual(result, [1, 2, 2])

    def test_fixture_already_sorted(self):
        """[1, 2, 3] → [1, 2, 3]  (zero shuffles needed; decisive transition on first check)."""
        import random; random.seed(0)
        from algorithms.sorting.bogo_sort import bogo_sort
        result = bogo_sort([1, 2, 3])
        self.assertEqual(result, [1, 2, 3])

    def test_fixture_reversed(self):
        """[3, 2, 1] → [1, 2, 3]  (fully reversed, seed 42)."""
        import random; random.seed(42)
        from algorithms.sorting.bogo_sort import bogo_sort
        result = bogo_sort([3, 2, 1])
        self.assertEqual(result, [1, 2, 3])

    def test_fixture_smallest_collection(self):
        """[1] → [1]  (single element: _is_sorted returns True immediately, no shuffle)."""
        from algorithms.sorting.bogo_sort import bogo_sort
        result = bogo_sort([1])
        self.assertEqual(result, [1])

    # ------------------------------------------------------------------
    # Mutation contract: same object returned
    # ------------------------------------------------------------------

    def test_returns_same_object(self):
        """bogo_sort returns the same list object it mutated (in-place + return)."""
        import random; random.seed(0)
        from algorithms.sorting.bogo_sort import bogo_sort
        arr = [3, 1, 2]
        result = bogo_sort(arr)
        self.assertIs(result, arr)
        self.assertEqual(arr, [1, 2, 3])

    # ------------------------------------------------------------------
    # Decisive state transition: already-sorted exits without any shuffle
    # ------------------------------------------------------------------

    def test_already_sorted_no_shuffle_needed(self):
        """Already-sorted input exits on first _is_sorted check; shuffle never called."""
        from algorithms.sorting.bogo_sort import bogo_sort
        from unittest.mock import patch
        arr = [1, 2, 3]
        with patch("random.shuffle") as mock_shuffle:
            result = bogo_sort(arr)
        mock_shuffle.assert_not_called()
        self.assertEqual(result, [1, 2, 3])

    def test_single_element_no_shuffle_needed(self):
        """Single-element list exits without any shuffle."""
        from algorithms.sorting.bogo_sort import bogo_sort
        from unittest.mock import patch
        with patch("random.shuffle") as mock_shuffle:
            result = bogo_sort([7])
        mock_shuffle.assert_not_called()
        self.assertEqual(result, [7])

    # ------------------------------------------------------------------
    # Docstring examples executed — displayed output asserted
    # ------------------------------------------------------------------

    def test_docstring_example_3_1_2(self):
        """Docstring example: seed(0) + [3,1,2] → [1,2,3] (displayed output asserted)."""
        import random; random.seed(0)
        from algorithms.sorting.bogo_sort import bogo_sort
        self.assertEqual(bogo_sort([3, 1, 2]), [1, 2, 3])

    def test_docstring_example_already_sorted(self):
        """Docstring example: seed(0) + [1,2,3] → [1,2,3]."""
        import random; random.seed(0)
        from algorithms.sorting.bogo_sort import bogo_sort
        self.assertEqual(bogo_sort([1, 2, 3]), [1, 2, 3])

    def test_docstring_example_2_2_1(self):
        """Docstring example: seed(0) + [2,2,1] → [1,2,2]."""
        import random; random.seed(0)
        from algorithms.sorting.bogo_sort import bogo_sort
        self.assertEqual(bogo_sort([2, 2, 1]), [1, 2, 2])

    def test_docstring_example_reversed_seed42(self):
        """Docstring example: seed(42) + [3,2,1] → [1,2,3]."""
        import random; random.seed(42)
        from algorithms.sorting.bogo_sort import bogo_sort
        self.assertEqual(bogo_sort([3, 2, 1]), [1, 2, 3])

    def test_docstring_example_single(self):
        """Docstring example: [1] → [1]."""
        from algorithms.sorting.bogo_sort import bogo_sort
        self.assertEqual(bogo_sort([1]), [1])


if __name__ == "__main__":
    unittest.main()
