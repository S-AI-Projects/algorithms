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


class TestRemoveMinRepeatable(unittest.TestCase):
    """remove_min has no hidden state: the same values give the same result.

    The fixture walks a plain list used as a stack (push A, B, C; pop twice;
    push D; drain) and calls remove_min on a copy at each state. A, B, C and
    D are small integers, so every input stays within list[int].
    """

    A, B, C, D = 3, 1, 2, 5

    EXPECTED = {
        "push A, B, C": [3, 2],  # [A, B, C] is [3, 1, 2]; B (1) is the minimum
        "pop twice": [],  # [A] is [3]; its only value is the minimum
        "push D": [5],  # [A, D] is [3, 5]; A (3) is the minimum
        "drain": [],  # documented empty-state behaviour: returned unchanged
        "pop order": [2, 1, 5, 3],  # C, B, D, A
    }

    def walk_fixture(self):
        """Run the fixture once from fresh state and return what it saw."""
        stack: list[int] = []
        popped: list[int] = []
        seen = {}
        for value in (self.A, self.B, self.C):
            stack.append(value)
        seen["push A, B, C"] = remove_min(list(stack))
        popped.append(stack.pop())
        popped.append(stack.pop())
        seen["pop twice"] = remove_min(list(stack))
        stack.append(self.D)
        seen["push D"] = remove_min(list(stack))
        while stack:
            popped.append(stack.pop())
        seen["drain"] = remove_min(stack)
        seen["pop order"] = popped
        return seen

    def test_fixture_walk(self):
        self.assertEqual(self.EXPECTED, self.walk_fixture())

    def test_fixture_twice_in_fresh_state(self):
        first = self.walk_fixture()
        second = self.walk_fixture()
        self.assertEqual(self.EXPECTED, first)
        self.assertEqual(self.EXPECTED, second)

    def test_fixture_after_another_valid_input(self):
        other = [4, 8, 3, 7, 3]
        self.assertEqual([4, 8, 7], remove_min(other))
        self.assertEqual(self.EXPECTED, self.walk_fixture())
        # The later run did not reach back into the earlier input either.
        self.assertEqual([4, 8, 7], other)

    def test_only_the_list_passed_in_changes(self):
        original = [2, 8, 3, -6, 7, 3]
        working_copy = list(original)
        result = remove_min(working_copy)
        self.assertIs(working_copy, result)
        self.assertEqual([2, 8, 3, 7, 3], working_copy)
        self.assertEqual([2, 8, 3, -6, 7, 3], original)

    def test_empty_stack_is_returned_unchanged(self):
        empty: list[int] = []
        self.assertIs(empty, remove_min(empty))
        self.assertEqual([], empty)


if __name__ == "__main__":
    unittest.main()
