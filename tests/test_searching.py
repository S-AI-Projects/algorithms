import unittest

from algorithms.searching import (
    binary_search,
    binary_search_recur,
    find_min_rotate,
    find_min_rotate_recur,
    first_occurrence,
    interpolation_search,
    jump_search,
    last_occurrence,
    linear_search,
    next_greatest_letter,
    next_greatest_letter_v1,
    next_greatest_letter_v2,
    search_insert,
    search_range,
    search_rotate,
    search_rotate_recur,
    ternary_search,
    two_sum,
    two_sum1,
    two_sum2,
)


class TestSuite(unittest.TestCase):
    def test_first_occurrence(self):
        def helper(array, query):
            idx = array.index(query) if query in array else -1
            return idx

        array = [1, 1, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6, 6, 6]
        self.assertEqual(first_occurrence(array, 1), helper(array, 1))
        self.assertEqual(first_occurrence(array, 3), helper(array, 3))
        self.assertEqual(first_occurrence(array, 5), helper(array, 5))
        self.assertEqual(first_occurrence(array, 6), helper(array, 6))
        self.assertEqual(first_occurrence(array, 7), helper(array, 7))
        self.assertEqual(first_occurrence(array, -1), helper(array, -1))

    def test_binary_search(self):
        array = [1, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6]
        self.assertEqual(10, binary_search(array, 5))
        self.assertEqual(11, binary_search(array, 6))
        self.assertEqual(-1, binary_search(array, 7))
        self.assertEqual(-1, binary_search(array, -1))
        # Test binary_search_recur
        self.assertEqual(10, binary_search_recur(array, 0, 11, 5))
        self.assertEqual(11, binary_search_recur(array, 0, 11, 6))
        self.assertEqual(-1, binary_search_recur(array, 0, 11, 7))
        self.assertEqual(-1, binary_search_recur(array, 0, 11, -1))

    def test_ternary_search(self):
        array = [1, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6]
        self.assertEqual(10, ternary_search(0, 11, 5, array))
        self.assertEqual(3, ternary_search(0, 10, 3, array))
        self.assertEqual(10, ternary_search(0, 10, 5, array))
        self.assertEqual(-1, ternary_search(0, 11, 7, array))
        self.assertEqual(-1, ternary_search(0, 11, -1, array))

    def test_last_occurrence(self):
        array = [1, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6, 6, 6]
        self.assertEqual(5, last_occurrence(array, 3))
        self.assertEqual(10, last_occurrence(array, 5))
        self.assertEqual(-1, last_occurrence(array, 7))
        self.assertEqual(0, last_occurrence(array, 1))
        self.assertEqual(13, last_occurrence(array, 6))

    def test_linear_search(self):
        array = [1, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6, 6, 6]
        self.assertEqual(6, linear_search(array, 4))
        self.assertEqual(10, linear_search(array, 5))
        self.assertEqual(-1, linear_search(array, 7))
        self.assertEqual(-1, linear_search(array, -1))

    def test_search_insert(self):
        array = [1, 3, 5, 6]
        self.assertEqual(2, search_insert(array, 5))
        self.assertEqual(1, search_insert(array, 2))
        self.assertEqual(4, search_insert(array, 7))
        self.assertEqual(0, search_insert(array, 0))

    def test_two_sum(self):
        array = [2, 7, 11, 15]
        # test two_sum
        self.assertEqual([1, 2], two_sum(array, 9))
        self.assertEqual([2, 4], two_sum(array, 22))
        # test two_sum1
        self.assertEqual([1, 2], two_sum1(array, 9))
        self.assertEqual([2, 4], two_sum1(array, 22))
        # test two_sum2
        self.assertEqual([1, 2], two_sum2(array, 9))
        self.assertEqual([2, 4], two_sum2(array, 22))

    def test_search_range(self):
        array = [5, 7, 7, 8, 8, 8, 10]
        self.assertEqual([3, 5], search_range(array, 8))
        self.assertEqual([1, 2], search_range(array, 7))
        self.assertEqual([-1, -1], search_range(array, 11))

        array = [5, 7, 7, 7, 7, 8, 8, 8, 8, 10]
        self.assertEqual([5, 8], search_range(array, 8))
        self.assertEqual([1, 4], search_range(array, 7))
        self.assertEqual([-1, -1], search_range(array, 11))

    def test_find_min_rotate(self):
        array = [4, 5, 6, 7, 0, 1, 2]
        self.assertEqual(0, find_min_rotate(array))
        array = [10, 20, -1, 0, 1, 2, 3, 4, 5]
        self.assertEqual(-1, find_min_rotate(array))
        # Test find min using recursion
        array = [4, 5, 6, 7, 0, 1, 2]
        self.assertEqual(0, find_min_rotate_recur(array, 0, 6))
        array = [10, 20, -1, 0, 1, 2, 3, 4, 5]
        self.assertEqual(-1, find_min_rotate_recur(array, 0, 8))

    def test_search_rotate(self):
        array = [15, 16, 19, 20, 25, 1, 3, 4, 5, 7, 10, 14]
        self.assertEqual(8, search_rotate(array, 5))
        self.assertEqual(-1, search_rotate(array, 9))
        self.assertEqual(8, search_rotate_recur(array, 0, 11, 5))
        self.assertEqual(-1, search_rotate_recur(array, 0, 11, 9))

    def test_jump_search(self):
        array = [1, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6]
        self.assertEqual(10, jump_search(array, 5))
        self.assertEqual(2, jump_search(array, 3))
        self.assertEqual(-1, jump_search(array, 7))
        self.assertEqual(-1, jump_search(array, -1))

    def test_next_greatest_letter(self):
        letters = ["c", "f", "j"]
        target = "a"
        self.assertEqual("c", next_greatest_letter(letters, target))
        self.assertEqual("c", next_greatest_letter_v1(letters, target))
        self.assertEqual("c", next_greatest_letter_v2(letters, target))
        letters = ["c", "f", "j"]
        target = "d"
        self.assertEqual("f", next_greatest_letter(letters, target))
        self.assertEqual("f", next_greatest_letter_v1(letters, target))
        self.assertEqual("f", next_greatest_letter_v2(letters, target))
        letters = ["c", "f", "j"]
        target = "j"
        self.assertEqual("c", next_greatest_letter(letters, target))
        self.assertEqual("c", next_greatest_letter_v1(letters, target))
        self.assertEqual("c", next_greatest_letter_v2(letters, target))

    def test_interpolation_search(self):
        array = [0, 3, 5, 5, 9, 12, 12, 15, 16, 19, 20]
        self.assertEqual(1, interpolation_search(array, 3))
        self.assertEqual(2, interpolation_search(array, 5))
        self.assertEqual(6, interpolation_search(array, 12))
        self.assertEqual(-1, interpolation_search(array, 22))
        self.assertEqual(-1, interpolation_search(array, -10))
        self.assertEqual(10, interpolation_search(array, 20))


class TestFindMinRotateCrossCheck(unittest.TestCase):
    """Cross-check find_min_rotate against an independent reference.

    Inputs are every rotation of sorted, duplicate-free lists of length 1-7.
    The expected minimum is known by construction (the first value of the
    sorted list) and confirmed with the built-in min(), a linear scan that
    does not call the function under test.
    """

    SORTED_VALUES = [-5, -2, 0, 3, 4, 9, 12]

    @classmethod
    def rotated_inputs(cls):
        cases = []
        for n in range(1, len(cls.SORTED_VALUES) + 1):
            base = cls.SORTED_VALUES[-n:]
            for k in range(n):
                cases.append((base[k:] + base[:k], base[0]))
        return cases

    def test_source_anchors(self):
        self.assertEqual(0, find_min_rotate([4, 5, 6, 7, 0, 1, 2]))
        self.assertEqual(1, find_min_rotate([1, 2, 3]))
        self.assertEqual(0, find_min_rotate_recur([4, 5, 6, 7, 0, 1, 2], 0, 6))

    def test_neighbouring_inputs(self):
        # First anchor rotated one more step left: the minimum is still 0.
        self.assertEqual(0, find_min_rotate([5, 6, 7, 0, 1, 2, 4]))
        # Second anchor rotated one step right: the minimum moves to index 1.
        self.assertEqual(1, find_min_rotate([3, 1, 2]))

    def test_matches_reference_on_every_small_rotation(self):
        cases = self.rotated_inputs()
        self.assertEqual(28, len(cases))
        for array, expected in cases:
            with self.subTest(array=array):
                self.assertEqual(expected, min(array))  # the oracle agrees
                self.assertEqual(expected, find_min_rotate(list(array)))

    def test_repeated_runs_on_fresh_inputs_agree_without_mutation(self):
        for array, expected in self.rotated_inputs():
            with self.subTest(array=array):
                first_input, second_input = list(array), list(array)
                self.assertEqual(expected, find_min_rotate(first_input))
                self.assertEqual(expected, find_min_rotate(second_input))
                self.assertEqual(array, first_input)
                self.assertEqual(array, second_input)


if __name__ == "__main__":
    unittest.main()
