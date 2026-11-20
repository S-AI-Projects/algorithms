import random
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


def _build(values):
    """Build a ListNode chain and return (head, nodes in original order)."""
    nodes = [ListNode(v) for v in values]
    for node, nxt in zip(nodes, nodes[1:], strict=False):
        node.next = nxt
    return (nodes[0] if nodes else None), nodes


def _walk(head, limit):
    """Return the nodes reachable from head, or None after more than limit."""
    seen = []
    while head is not None:
        if len(seen) == limit + 1:
            return None
        seen.append(head)
        head = head.next
    return seen


def _reverse_violation(reverse, values):
    """Check the reverse_list invariant for one input.

    Returns None when it holds, else a description of the first violation.
    Links are checked by node identity and values separately, so a
    value-only comparison cannot hide a broken link.
    """
    head, nodes = _build(values)
    walked = _walk(reverse(head), len(nodes))
    if walked is None:
        return "traversal did not terminate"
    if len(walked) != len(nodes):
        return f"expected {len(nodes)} nodes, reached {len(walked)}"
    if any(a is not b for a, b in zip(walked, reversed(nodes), strict=True)):
        return "result is not the original nodes in reverse order"
    if [node.val for node in walked] != list(reversed(values)):
        return "node values changed"
    if nodes and nodes[0].next is not None:
        return "old head is not the tail"
    return None


class TestReverseListInvariant(unittest.TestCase):
    """Invariant tests for reverse_list (R24-T044).

    Invariant: for input n0 -> ... -> nk, the result is the same node
    objects linked nk -> ... -> n0 -> None, each exactly once, with values
    unchanged. Only finite, acyclic lists of ListNode are generated, which is
    the supported input domain.
    """

    SEED = 44
    CASES = 200

    def test_three_distinct_nodes_links(self):
        a, b, c = ListNode("A"), ListNode("B"), ListNode("C")
        a.next, b.next = b, c
        result = reverse_list(a)
        self.assertIs(result, c)
        self.assertIs(c.next, b)
        self.assertIs(b.next, a)
        self.assertIsNone(a.next)

    def test_three_distinct_nodes_values(self):
        a, b, c = ListNode("A"), ListNode("B"), ListNode("C")
        a.next, b.next = b, c
        result = reverse_list(a)
        self.assertEqual(convert(result), ["C", "B", "A"])
        self.assertEqual([a.val, b.val, c.val], ["A", "B", "C"])

    def test_empty_list(self):
        self.assertIsNone(reverse_list(None))

    def test_single_node(self):
        node = ListNode(1)
        self.assertIs(reverse_list(node), node)
        self.assertIsNone(node.next)
        self.assertEqual(node.val, 1)

    def test_duplicate_values_checked_by_identity(self):
        head, nodes = _build([7, 7, 7])
        walked = _walk(reverse_list(head), 3)
        self.assertEqual([node.val for node in walked], [7, 7, 7])
        self.assertEqual([id(n) for n in walked], [id(n) for n in nodes[::-1]])

    def test_reverse_twice_restores_order(self):
        head, nodes = _build([1, 2, 3, 4])
        restored = reverse_list(reverse_list(head))
        self.assertIs(restored, nodes[0])
        self.assertEqual(convert(restored), [1, 2, 3, 4])

    def test_invariant_on_seeded_cases(self):
        rng = random.Random(self.SEED)
        cases = [[1, 2, 3]]  # readable small case first
        while len(cases) < self.CASES:
            length = rng.randint(0, 25)
            cases.append([rng.randint(-3, 3) for _ in range(length)])
        failures = [
            (values, problem)
            for values in cases
            if (problem := _reverse_violation(reverse_list, values)) is not None
        ]
        smallest = min(failures, key=lambda f: len(f[0]), default=None)
        self.assertIsNone(smallest, f"smallest failing case: {smallest}")
        self.assertEqual(len(cases), 200)

    def test_invariant_rejects_value_only_reverse(self):
        # A broken "reverse" that swaps values but keeps the links passes a
        # value-only comparison; the invariant must still reject it.
        def reverse_values_only(head):
            nodes = _walk(head, 100)
            values = [node.val for node in nodes]
            for node, value in zip(nodes, reversed(values), strict=True):
                node.val = value
            return head

        self.assertEqual(
            _reverse_violation(reverse_values_only, [1, 2, 3]),
            "result is not the original nodes in reverse order",
        )


if __name__ == "__main__":
    unittest.main()
