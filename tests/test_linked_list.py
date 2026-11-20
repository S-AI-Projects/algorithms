import unittest

from algorithms.common import ListNode
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


def _values(head):
    """Walk a list iteratively and return its values."""
    values = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


class TestListNodeBoundaries(unittest.TestCase):
    """Boundary tests for algorithms.common.ListNode (R24-T042).

    Each test sits on one side of a boundary documented in the ListNode
    docstring. Expected values were worked out by hand from that contract.
    """

    def test_anchor_three_node_list(self):
        head = ListNode(1, ListNode(2, ListNode(3)))
        self.assertEqual(head.val, 1)
        self.assertEqual(head.next.val, 2)
        self.assertEqual(head.next.next.val, 3)
        self.assertIsNone(head.next.next.next)

    def test_neighbor_prepend_to_anchor(self):
        # Prepending 0 to the anchor gives 0 -> 1 -> 2 -> 3.
        head = ListNode(1, ListNode(2, ListNode(3)))
        new_head = ListNode(0, head)
        self.assertEqual(_values(new_head), [0, 1, 2, 3])
        self.assertIs(new_head.next, head)
        self.assertEqual(_values(head), [1, 2, 3])

    def test_default_node_is_smallest_list(self):
        node = ListNode()
        self.assertEqual(node.val, 0)
        self.assertIsNone(node.next)
        self.assertEqual(_values(node), [0])

    def test_single_node_has_no_next(self):
        node = ListNode(7)
        self.assertIsNone(node.next)
        self.assertEqual(node, ListNode(7, None))
        self.assertEqual(_values(node), [7])

    def test_keyword_arguments(self):
        node = ListNode(next=ListNode(5), val=4)
        self.assertEqual(_values(node), [4, 5])

    def test_zero_value_node_is_truthy(self):
        node = ListNode(0)
        self.assertTrue(node)
        self.assertEqual(node.val, 0)

    def test_equality_same_values_same_length(self):
        self.assertEqual(ListNode(1, ListNode(2)), ListNode(1, ListNode(2)))

    def test_equality_different_length(self):
        self.assertNotEqual(ListNode(1), ListNode(1, ListNode(2)))
        self.assertNotEqual(ListNode(1, ListNode(2)), ListNode(1))

    def test_equality_different_tail_value(self):
        self.assertNotEqual(ListNode(1, ListNode(2)), ListNode(1, ListNode(3)))

    def test_equality_with_non_node(self):
        self.assertFalse(ListNode(1) == 1)
        self.assertFalse(ListNode(0) == 0)

    def test_next_is_not_copied(self):
        tail = ListNode(2)
        head = ListNode(1, tail)
        self.assertIs(head.next, tail)
        tail.val = 9
        self.assertEqual(_values(head), [1, 9])

    def test_relinking_next(self):
        head = ListNode(1, ListNode(2, ListNode(3)))
        head.next = head.next.next
        self.assertEqual(_values(head), [1, 3])
        head.next = None
        self.assertEqual(_values(head), [1])

    def test_repr(self):
        self.assertEqual(repr(ListNode()), "ListNode(val=0, next=None)")
        self.assertEqual(
            repr(ListNode(1, ListNode(2))),
            "ListNode(val=1, next=ListNode(val=2, next=None))",
        )

    def test_repr_of_cycle(self):
        node = ListNode(1)
        node.next = node
        self.assertEqual(repr(node), "ListNode(val=1, next=...)")

    def test_nodes_are_unhashable(self):
        with self.assertRaises(TypeError):
            hash(ListNode())


if __name__ == "__main__":
    unittest.main()
