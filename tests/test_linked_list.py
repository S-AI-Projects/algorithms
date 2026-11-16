import random
import unittest

from algorithms.linked_list import (
    RandomListNode,
    copy_random_pointer_v1,
    copy_random_pointer_v2,
    is_cyclic,
    is_palindrome,
    is_palindrome_dict,
    is_palindrome_stack,
    is_sorted,
    merge_two_list,
    merge_two_list_recur,
    remove_range,
    reverse_list,
    reverse_list_recursive,
    rotate_right,
    swap_pairs,
)
from algorithms.linked_list.add_two_numbers import Node as DigitNode
from algorithms.linked_list.add_two_numbers import add_two_numbers, convert_to_str


class Node:
    def __init__(self, x):
        self.val = x
        self.next = None


# Convert from linked list Node to list for testing
def convert(head):
    ret = []
    if head:
        current = head
        while current:
            ret.append(current.val)
            current = current.next
    return ret


class TestSuite(unittest.TestCase):
    def setUp(self):
        # list test for palindrome
        self.l = Node("A")
        self.l.next = Node("B")
        self.l.next.next = Node("C")
        self.l.next.next.next = Node("B")
        self.l.next.next.next.next = Node("A")

        self.l1 = Node("A")
        self.l1.next = Node("B")
        self.l1.next.next = Node("C")
        self.l1.next.next.next = Node("B")

    def test_reverse_list(self):
        head = Node(1)
        head.next = Node(2)
        head.next.next = Node(3)
        head.next.next.next = Node(4)
        self.assertEqual([4, 3, 2, 1], convert(reverse_list(head)))
        head = Node(1)
        head.next = Node(2)
        head.next.next = Node(3)
        head.next.next.next = Node(4)
        self.assertEqual([4, 3, 2, 1], convert(reverse_list_recursive(head)))

    def test_is_sorted(self):
        head = Node(-2)
        head.next = Node(2)
        head.next.next = Node(2)
        head.next.next.next = Node(4)
        head.next.next.next.next = Node(9)
        # head -> -2 -> 2 -> 2 -> 4 -> 9
        self.assertTrue(is_sorted(head))
        head = Node(1)
        head.next = Node(2)
        head.next.next = Node(8)
        head.next.next.next = Node(4)
        head.next.next.next.next = Node(6)
        # head -> 1 -> 2 -> 8 -> 4 -> 6
        self.assertFalse(is_sorted(head))

    def test_remove_range(self):
        # Test case: middle case.
        head = Node(0)
        head.next = Node(1)
        head.next.next = Node(2)
        head.next.next.next = Node(3)
        head.next.next.next.next = Node(4)
        # Expect output: 0 4
        self.assertEqual([0, 4], convert(remove_range(head, 1, 3)))

        # Test case: taking out the front node
        head = Node(0)
        head.next = Node(1)
        head.next.next = Node(2)
        head.next.next.next = Node(3)
        head.next.next.next.next = Node(4)
        # Expect output: 2 3 4
        self.assertEqual([2, 3, 4], convert(remove_range(head, 0, 1)))

        # Test case: removing all the nodes
        head = Node(0)
        head.next = Node(1)
        head.next.next = Node(2)
        head.next.next.next = Node(3)
        head.next.next.next.next = Node(4)
        self.assertEqual([], convert(remove_range(head, 0, 7)))

    def test_swap_in_pairs(self):
        head = Node(1)
        head.next = Node(2)
        head.next.next = Node(3)
        head.next.next.next = Node(4)
        # Expect output : 2 --> 1 --> 4 --> 3
        self.assertEqual([2, 1, 4, 3], convert(swap_pairs(head)))

    def test_rotate_right(self):
        # Given 1->2->3->4->5->NULL
        head = Node(1)
        head.next = Node(2)
        head.next.next = Node(3)
        head.next.next.next = Node(4)
        head.next.next.next.next = Node(5)
        # K = 2. Expect output: 4->5->1->2->3->NULL.
        self.assertEqual([4, 5, 1, 2, 3], convert(rotate_right(head, 2)))

    def test_is_cyclic(self):
        # create linked list => A -> B -> C -> D -> E -> C
        head = Node("A")
        head.next = Node("B")
        curr = head.next
        cyclic_node = Node("C")
        curr.next = cyclic_node
        curr = curr.next
        curr.next = Node("D")
        curr = curr.next
        curr.next = Node("E")
        curr = curr.next
        curr.next = cyclic_node
        self.assertTrue(is_cyclic(head))

        # create linked list 1 -> 2 -> 3 -> 4
        head = Node(1)
        curr = head
        for i in range(2, 6):
            curr.next = Node(i)
            curr = curr.next
        self.assertFalse(is_cyclic(head))

    def test_merge_two_list(self):
        """
        Input: head1:1->2->4, head2: 1->3->4
        Output: 1->1->2->3->4->4
        """
        head1 = Node(1)
        head1.next = Node(2)
        head1.next.next = Node(4)
        head2 = Node(1)
        head2.next = Node(3)
        head2.next.next = Node(4)
        self.assertEqual([1, 1, 2, 3, 4, 4], convert(merge_two_list(head1, head2)))
        # Test recursive
        head1 = Node(1)
        head1.next = Node(2)
        head1.next.next = Node(4)
        head2 = Node(1)
        head2.next = Node(3)
        head2.next.next = Node(4)
        self.assertEqual(
            [1, 1, 2, 3, 4, 4], convert(merge_two_list_recur(head1, head2))
        )

    def test_is_palindrome(self):
        self.assertTrue(is_palindrome(self.l))
        self.assertFalse(is_palindrome(self.l1))

    def test_is_palindrome_stack(self):
        self.assertTrue(is_palindrome_stack(self.l))
        self.assertFalse(is_palindrome_stack(self.l1))

    def test_is_palindrome_dict(self):
        self.assertTrue(is_palindrome_dict(self.l))
        self.assertFalse(is_palindrome_dict(self.l1))

    def test_solution_0(self):
        self._init_random_list_nodes()
        result = copy_random_pointer_v1(self.random_list_node1)
        self._assert_is_a_copy(result)

    def test_solution_1(self):
        self._init_random_list_nodes()
        result = copy_random_pointer_v2(self.random_list_node1)
        self._assert_is_a_copy(result)

    def _assert_is_a_copy(self, result):
        self.assertEqual(5, result.next.next.next.next.label)
        self.assertEqual(4, result.next.next.next.label)
        self.assertEqual(3, result.next.next.label)
        self.assertEqual(2, result.next.label)
        self.assertEqual(1, result.label)
        self.assertEqual(3, result.next.next.next.next.random.label)
        self.assertIsNone(result.next.next.next.random)
        self.assertEqual(2, result.next.next.random.label)
        self.assertEqual(5, result.next.random.label)
        self.assertEqual(4, result.random.label)

    def _init_random_list_nodes(self):
        self.random_list_node1 = RandomListNode(1)
        random_list_node2 = RandomListNode(2)
        random_list_node3 = RandomListNode(3)
        random_list_node4 = RandomListNode(4)
        random_list_node5 = RandomListNode(5)

        self.random_list_node1.next, self.random_list_node1.random = (
            random_list_node2,
            random_list_node4,
        )
        random_list_node2.next, random_list_node2.random = (
            random_list_node3,
            random_list_node5,
        )
        random_list_node3.next, random_list_node3.random = (
            random_list_node4,
            random_list_node2,
        )
        random_list_node4.next = random_list_node5
        random_list_node5.random = random_list_node3


class TestAddTwoNumbersNodeInvariant(unittest.TestCase):
    """Invariant of Node in algorithms/linked_list/add_two_numbers.py.

    Following ``next`` from a head stops at None and visits each node once.
    The module's functions only read the nodes they are given and return
    lists built from new nodes. Values and links are checked separately:
    links by identity, so a value-only comparison cannot hide a broken link.
    """

    SEED = 24024
    RANDOM_CASES = 200
    READABLE_CASES = [(0, 0), (5, 7), (342, 465)]

    @staticmethod
    def build(digits):
        """Link one new DigitNode per digit and return (head, nodes)."""
        nodes = [DigitNode(digit) for digit in digits]
        # The last node has no successor, so the lengths differ by one.
        for node, successor in zip(nodes, nodes[1:], strict=False):
            node.next = successor
        return nodes[0], nodes

    @staticmethod
    def walk(head, limit):
        """Follow next from head; fail instead of looping on a cycle."""
        visited = []
        node = head
        while node is not None:
            if len(visited) == limit:
                raise AssertionError(f"traversal did not stop within {limit} nodes")
            visited.append(node)
            node = node.next
        return visited

    @staticmethod
    def ids(nodes):
        return [id(node) for node in nodes]

    @staticmethod
    def state(nodes):
        """Each node's value and the identity of its successor."""
        return [(node.val, id(node.next)) for node in nodes]

    def test_fixture_three_distinct_nodes(self):
        a, b, c = DigitNode(2), DigitNode(4), DigitNode(3)
        a.next = b
        b.next = c
        # Links, checked by identity.
        self.assertIs(b, a.next)
        self.assertIs(c, b.next)
        self.assertIsNone(c.next)
        # Values, checked separately.
        self.assertEqual([2, 4, 3], [a.val, b.val, c.val])
        # Traversal visits A, B, C once each, in order, then stops.
        self.assertEqual(self.ids([a, b, c]), self.ids(self.walk(a, 3)))
        # Reading the list reports its digits and leaves every link alone.
        self.assertEqual("243", convert_to_str(a))
        self.assertIs(b, a.next)
        self.assertIs(c, b.next)
        self.assertIsNone(c.next)

    def test_fixture_smallest_supported_list(self):
        only = DigitNode(5)
        self.assertIsNone(only.next)
        self.assertEqual(5, only.val)
        self.assertEqual(self.ids([only]), self.ids(self.walk(only, 1)))
        self.assertEqual("5", convert_to_str(only))
        self.assertIsNone(only.next)

    def test_fixture_sum_is_built_from_new_nodes(self):
        # 342 + 5 = 347, stored least significant digit first.
        a, inputs_left = self.build([2, 4, 3])
        d = DigitNode(5)
        inputs = inputs_left + [d]
        before = self.state(inputs)
        # Check the inputs stop at None first, so a cycle fails, not hangs.
        self.assertEqual(self.ids(inputs_left), self.ids(self.walk(a, 3)))
        self.assertIsNone(d.next)
        result = self.walk(add_two_numbers(a, d), 3)
        self.assertEqual([7, 4, 3], [node.val for node in result])
        self.assertEqual(3, len(set(self.ids(result))))
        self.assertEqual(set(), set(self.ids(result)) & set(self.ids(inputs)))
        self.assertEqual(before, self.state(inputs))

    def check_case(self, left_number, right_number):
        left_digits = [int(ch) for ch in reversed(str(left_number))]
        right_digits = [int(ch) for ch in reversed(str(right_number))]
        left, left_nodes = self.build(left_digits)
        right, right_nodes = self.build(right_digits)
        inputs = left_nodes + right_nodes
        before = self.state(inputs)

        # Each input visits its own nodes once each, then stops.
        self.assertEqual(
            self.ids(left_nodes), self.ids(self.walk(left, len(left_nodes)))
        )
        self.assertEqual(
            self.ids(right_nodes), self.ids(self.walk(right, len(right_nodes)))
        )
        self.assertEqual("".join(map(str, left_digits)), convert_to_str(left))

        # The sum is a new list: right digits, each node once, no input node.
        expected = [int(ch) for ch in reversed(str(left_number + right_number))]
        result = self.walk(add_two_numbers(left, right), len(expected) + 1)
        self.assertEqual(expected, [node.val for node in result])
        self.assertEqual(len(result), len(set(self.ids(result))))
        self.assertEqual(set(), set(self.ids(result)) & set(self.ids(inputs)))

        # Every input node keeps its value and its link.
        self.assertEqual(before, self.state(inputs))

    def test_property_readable_small_cases(self):
        for left_number, right_number in self.READABLE_CASES:
            with self.subTest(left=left_number, right=right_number):
                self.check_case(left_number, right_number)

    def test_property_seeded_random_cases(self):
        rng = random.Random(self.SEED)
        for case in range(self.RANDOM_CASES):
            left_number = rng.randrange(10 ** rng.randint(1, 12))
            right_number = rng.randrange(10 ** rng.randint(1, 12))
            with self.subTest(case=case, left=left_number, right=right_number):
                self.check_case(left_number, right_number)


if __name__ == "__main__":
    unittest.main()
