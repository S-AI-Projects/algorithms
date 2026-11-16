import unittest

from algorithms.stack import (
    ArrayStack,
    LinkedListStack,
    OrderedStack,
    first_is_consecutive,
    first_stutter,
    first_switch_pairs,
    is_sorted,
    is_valid,
    remove_min,
    second_is_consecutive,
    second_stutter,
    second_switch_pairs,
    simplify_path,
)


class TestSuite(unittest.TestCase):
    def test_is_consecutive(self):
        self.assertTrue(first_is_consecutive([3, 4, 5, 6, 7]))
        self.assertFalse(first_is_consecutive([3, 4, 6, 7]))
        self.assertFalse(first_is_consecutive([3, 2, 1]))

        self.assertTrue(second_is_consecutive([3, 4, 5, 6, 7]))
        self.assertFalse(second_is_consecutive([3, 4, 6, 7]))
        self.assertFalse(second_is_consecutive([3, 2, 1]))

    def test_is_sorted(self):
        # Test case: bottom [6, 3, 5, 1, 2, 4] top
        self.assertFalse(is_sorted([6, 3, 5, 1, 2, 4]))
        self.assertTrue(is_sorted([1, 2, 3, 4, 5, 6]))
        self.assertFalse(is_sorted([3, 4, 7, 8, 5, 6]))

        # Stack must be preserved after the call (True case only)
        stack = [1, 2, 3, 6]
        is_sorted(stack)
        self.assertEqual([1, 2, 3, 6], stack)
        # Edge case: single element
        stack = [5]
        is_sorted(stack)
        self.assertEqual([5], stack)

    def test_remove_min(self):
        # Test case: bottom [2, 8, 3, -6, 7, 3] top
        self.assertEqual([2, 8, 3, 7, 3], remove_min([2, 8, 3, -6, 7, 3]))
        # Test case: 2 smallest value [2, 8, 3, 7, 3]
        self.assertEqual([4, 8, 7], remove_min([4, 8, 3, 7, 3]))

    def test_stutter(self):
        # Test case: bottom [3, 7, 1, 14, 9] top
        self.assertEqual(
            [3, 3, 7, 7, 1, 1, 14, 14, 9, 9], first_stutter([3, 7, 1, 14, 9])
        )
        self.assertEqual(
            [3, 3, 7, 7, 1, 1, 14, 14, 9, 9], second_stutter([3, 7, 1, 14, 9])
        )

    def test_switch_pairs(self):
        # Test case: even number of values in stack
        # bottom [3, 8, 17, 9, 1, 10] top
        self.assertEqual([8, 3, 9, 17, 10, 1], first_switch_pairs([3, 8, 17, 9, 1, 10]))
        self.assertEqual(
            [8, 3, 9, 17, 10, 1], second_switch_pairs([3, 8, 17, 9, 1, 10])
        )
        # Test case: odd number of values in stack
        # bottom [3, 8, 17, 9, 1] top
        self.assertEqual([8, 3, 9, 17, 1], first_switch_pairs([3, 8, 17, 9, 1]))
        self.assertEqual([8, 3, 9, 17, 1], second_switch_pairs([3, 8, 17, 9, 1]))

    def test_is_valid_parenthesis(self):

        self.assertTrue(is_valid("[]"))
        self.assertTrue(is_valid("[]()[]"))
        self.assertFalse(is_valid("[[[]]"))
        self.assertTrue(is_valid("{([])}"))
        self.assertFalse(is_valid("(}"))

    def test_simplify_path(self):
        p = "/my/name/is/..//keon"
        self.assertEqual("/my/name/keon", simplify_path(p))


class TestFirstSwitchPairsBoundaries(unittest.TestCase):
    """Boundary contract of first_switch_pairs (index 0 is the stack bottom)."""

    def test_fixture_walk_on_list_stack(self):
        # Fixture: push A, B, C; pop twice; push D; drain.
        # Expected pop order: C, B, D, A. At each state, first_switch_pairs
        # runs on a copy so the fixture stack itself is not disturbed.
        stack: list[str] = []
        popped: list[str] = []
        for value in ("A", "B", "C"):
            stack.append(value)
        self.assertEqual(["A", "B", "C"], stack)
        self.assertEqual(["B", "A", "C"], first_switch_pairs(list(stack)))

        popped.append(stack.pop())
        popped.append(stack.pop())
        self.assertEqual(["A"], stack)
        self.assertEqual(["A"], first_switch_pairs(list(stack)))

        stack.append("D")
        self.assertEqual(["A", "D"], stack)
        self.assertEqual(["D", "A"], first_switch_pairs(list(stack)))

        while stack:
            popped.append(stack.pop())
        self.assertEqual(["C", "B", "D", "A"], popped)

        # Documented empty-state behaviour on the drained stack.
        self.assertEqual([], first_switch_pairs(stack))
        self.assertEqual([], stack)

    def test_empty_stack_returns_empty_without_error(self):
        self.assertEqual([], first_switch_pairs([]))

    def test_single_value_is_not_moved(self):
        self.assertEqual([7], first_switch_pairs([7]))

    def test_two_values_are_swapped(self):
        self.assertEqual([2, 1], first_switch_pairs([1, 2]))

    def test_odd_count_leaves_top_value_in_place(self):
        self.assertEqual([2, 1, 3], first_switch_pairs([1, 2, 3]))

    def test_even_count_swaps_every_pair(self):
        self.assertEqual([2, 1, 4, 3], first_switch_pairs([1, 2, 3, 4]))

    def test_rearranges_input_in_place_and_returns_it(self):
        stack = [1, 2, 3, 4]
        result = first_switch_pairs(stack)
        self.assertIs(stack, result)
        self.assertEqual([2, 1, 4, 3], stack)


class TestStack(unittest.TestCase):
    def test_array_stack(self):
        stack = ArrayStack()
        stack.push(1)
        stack.push(2)
        stack.push(3)

        # test __iter__()
        it = iter(stack)
        self.assertEqual(3, next(it))
        self.assertEqual(2, next(it))
        self.assertEqual(1, next(it))
        self.assertRaises(StopIteration, next, it)

        # test __len__()
        self.assertEqual(3, len(stack))

        # test __str__()
        self.assertEqual(str(stack), "Top-> 3 2 1")

        # test is_empty()
        self.assertFalse(stack.is_empty())

        # test peek()
        self.assertEqual(3, stack.peek())

        # test pop()
        self.assertEqual(3, stack.pop())
        self.assertEqual(2, stack.pop())
        self.assertEqual(1, stack.pop())

        self.assertTrue(stack.is_empty())

    def test_linked_list_stack(self):
        stack = LinkedListStack()

        stack.push(1)
        stack.push(2)
        stack.push(3)

        # test __iter__()
        it = iter(stack)
        self.assertEqual(3, next(it))
        self.assertEqual(2, next(it))
        self.assertEqual(1, next(it))
        self.assertRaises(StopIteration, next, it)

        # test __len__()
        self.assertEqual(3, len(stack))

        # test __str__()
        self.assertEqual(str(stack), "Top-> 3 2 1")

        # test is_empty()
        self.assertFalse(stack.is_empty())

        # test peek()
        self.assertEqual(3, stack.peek())

        # test pop()
        self.assertEqual(3, stack.pop())
        self.assertEqual(2, stack.pop())
        self.assertEqual(1, stack.pop())

        self.assertTrue(stack.is_empty())


class TestOrderedStack(unittest.TestCase):
    def test_ordered_stack(self):
        stack = OrderedStack()
        self.assertTrue(stack.is_empty())
        stack.push(1)
        stack.push(4)
        stack.push(3)
        stack.push(6)
        "bottom - > 1 3 4 6 "
        self.assertEqual(6, stack.pop())
        self.assertEqual(4, stack.peek())
        self.assertEqual(3, stack.size())


if __name__ == "__main__":
    unittest.main()
