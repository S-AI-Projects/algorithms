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


class TestRandomListNodeBoundaries(unittest.TestCase):
    """Boundary and contract test suite for RandomListNode and copy_random_pointer."""

    def test_random_list_node_initialization_and_boundaries(self):
        # Valid interior: integer label
        node = RandomListNode(42)
        self.assertEqual(node.label, 42)
        self.assertIsNone(node.next)
        self.assertIsNone(node.random)

        # Valid boundary: falsy integer label 0
        node_zero = RandomListNode(0)
        self.assertEqual(node_zero.label, 0)

        # Valid boundary: negative integer label
        node_neg = RandomListNode(-7)
        self.assertEqual(node_neg.label, -7)

        # Valid boundary: string label supported via duck typing
        node_str = RandomListNode("A")
        self.assertEqual(node_str.label, "A")

        # Explicitly unsupported boundary: missing required label argument
        with self.assertRaises(TypeError):
            RandomListNode()  # type: ignore[call-arg]

    def test_fixture_three_nodes_separate_value_and_link_checks(self):
        # Fixture: construct three distinct nodes A -> B -> C
        node_a = RandomListNode("A")
        node_b = RandomListNode("B")
        node_c = RandomListNode("C")
        node_a.next = node_b
        node_b.next = node_c
        node_c.next = None
        # Non-trivial random pointer assignments: A->C, B->A, C->None
        node_a.random = node_c
        node_b.random = node_a
        node_c.random = None

        for copy_fn in (copy_random_pointer_v1, copy_random_pointer_v2):
            with self.subTest(copy_fn=copy_fn.__name__):
                copied_head = copy_fn(node_a)
                self.assertIsNotNone(copied_head)
                copied_b = copied_head.next
                copied_c = copied_b.next if copied_b else None

                # 1. Check values separately
                self.assertEqual(copied_head.label, "A")
                self.assertEqual(copied_b.label, "B")
                self.assertEqual(copied_c.label, "C")

                # 2. Check node links separately (distinct instances, correct structure)
                self.assertIsNot(copied_head, node_a)
                self.assertIsNot(copied_b, node_b)
                self.assertIsNot(copied_c, node_c)

                # Next pointers
                self.assertIs(copied_head.next, copied_b)
                self.assertIs(copied_b.next, copied_c)
                self.assertIsNone(copied_c.next)

                # Random pointers
                self.assertIs(copied_head.random, copied_c)
                self.assertIs(copied_b.random, copied_head)
                self.assertIsNone(copied_c.random)

                # 3. Verify original list was not mutated
                self.assertEqual(node_a.label, "A")
                self.assertEqual(node_b.label, "B")
                self.assertEqual(node_c.label, "C")
                self.assertIs(node_a.next, node_b)
                self.assertIs(node_b.next, node_c)
                self.assertIsNone(node_c.next)
                self.assertIs(node_a.random, node_c)
                self.assertIs(node_b.random, node_a)
                self.assertIsNone(node_c.random)

    def test_smallest_supported_list_empty(self):
        # Smallest supported list: None (empty list)
        self.assertIsNone(copy_random_pointer_v1(None))
        self.assertIsNone(copy_random_pointer_v2(None))

    def test_smallest_supported_list_single_node(self):
        # Smallest non-empty list: single node with no next/random links
        single = RandomListNode(1)
        for copy_fn in (copy_random_pointer_v1, copy_random_pointer_v2):
            with self.subTest(copy_fn=copy_fn.__name__):
                copied = copy_fn(single)
                self.assertIsNotNone(copied)
                self.assertIsNot(copied, single)
                self.assertEqual(copied.label, 1)
                self.assertIsNone(copied.next)
                self.assertIsNone(copied.random)

    def test_single_node_self_referential_random(self):
        # Single node with random pointing to itself
        single = RandomListNode(99)
        single.random = single
        for copy_fn in (copy_random_pointer_v1, copy_random_pointer_v2):
            with self.subTest(copy_fn=copy_fn.__name__):
                copied = copy_fn(single)
                self.assertIsNotNone(copied)
                self.assertIsNot(copied, single)
                self.assertEqual(copied.label, 99)
                self.assertIsNone(copied.next)
                self.assertIs(copied.random, copied)

    def test_boundary_falsy_label_zero_preserved(self):
        # Node with label 0
        node = RandomListNode(0)
        for copy_fn in (copy_random_pointer_v1, copy_random_pointer_v2):
            with self.subTest(copy_fn=copy_fn.__name__):
                copied = copy_fn(node)
                self.assertIsNotNone(copied)
                self.assertIsNot(copied, node)
                self.assertEqual(copied.label, 0)


if __name__ == "__main__":
    unittest.main()
