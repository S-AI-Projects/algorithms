import doctest
import importlib
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


class _FlipRecorder(list):
    """A list that records its contents after every slice assignment.

    pancake_sort changes the list only through ``array[...] = reversed(...)``,
    so each recorded state is the list right after one flip.
    """

    def __init__(self, values):
        super().__init__(values)
        self.states = []

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self.states.append(list(self))


class TestPancakeSortWorkedExample(unittest.TestCase):
    """Executable worked example for pancake_sort (R24-T047)."""

    # input -> (state after each flip, worked out by hand; final result)
    TRACES = {
        (3, 1, 2): ([[2, 1, 3], [1, 2, 3]], [1, 2, 3]),
        (1, 3, 2): ([[3, 1, 2], [2, 1, 3], [1, 2, 3]], [1, 2, 3]),
        (2, 2, 1): ([[1, 2, 2]], [1, 2, 2]),
        (1, 2, 3): ([], [1, 2, 3]),
        (3, 2, 1): ([[1, 2, 3]], [1, 2, 3]),
        (): ([], []),
        (5,): ([], [5]),
    }

    def test_docstring_examples_run_and_match(self):
        module = importlib.import_module("algorithms.sorting.pancake_sort")
        results = doctest.testmod(module, verbose=False)
        self.assertEqual(results.failed, 0)
        self.assertEqual(results.attempted, 10)

    def test_flip_states_match_hand_trace(self):
        for values, (expected_states, expected_result) in self.TRACES.items():
            with self.subTest(values=list(values)):
                recorder = _FlipRecorder(values)
                result = pancake_sort(recorder)
                self.assertEqual(recorder.states, expected_states)
                self.assertEqual(list(result), expected_result)

    def test_sorted_suffix_grows_by_one_each_pass(self):
        # Decisive transition: the pass for cur=3 ends with its second flip
        # (state 2), which puts 3 at index 2. Index 2 never changes after.
        recorder = _FlipRecorder([1, 3, 2])
        pancake_sort(recorder)
        self.assertEqual(recorder.states[0], [3, 1, 2])  # max flipped to front
        self.assertEqual(recorder.states[1], [2, 1, 3])  # max flipped into place
        self.assertEqual([state[2] for state in recorder.states[1:]], [3, 3])
        self.assertEqual(recorder.states[-1], [1, 2, 3])

    def test_fixture_results(self):
        self.assertEqual(pancake_sort([3, 1, 2]), [1, 2, 3])
        self.assertEqual(pancake_sort([2, 2, 1]), [1, 2, 2])
        self.assertEqual(pancake_sort([1, 2, 3]), [1, 2, 3])
        self.assertEqual(pancake_sort([3, 2, 1]), [1, 2, 3])
        self.assertEqual(pancake_sort([]), [])

    def test_sorts_in_place_and_returns_same_list(self):
        for values in ([3, 1, 2], [], [5]):
            with self.subTest(values=values):
                data = list(values)
                self.assertIs(pancake_sort(data), data)
        data = [2, 2, 1]
        pancake_sort(data)
        self.assertEqual(data, [1, 2, 2])


if __name__ == "__main__":
    unittest.main()
