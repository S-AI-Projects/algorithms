# ListNode boundary table (R24-T042)

Source: `algorithms/common/list_node.py` (docstring contract and dataclass fields).

| Boundary | Side | Check | Expected | Actual | Source |
|---|---|---|---|---|---|
| anchor | interior | `ListNode(1, ListNode(2, ListNode(3))).val` | `1` | `1` | algorithms/common/list_node.py L49-L51 |
| anchor | interior | `ListNode(1, ListNode(2, ListNode(3))).next.val` | `2` | `2` | algorithms/common/list_node.py L49, L52-L53 |
| neighbor | interior | `values(ListNode(0, head)), values(head)` | `[[0, 1, 2, 3], [1, 2, 3]]` | `[[0, 1, 2, 3], [1, 2, 3]]` | algorithms/common/list_node.py L23-L26 |
| construction | boundary | `(ListNode().val, ListNode().next)` | `[0, None]` | `[0, None]` | algorithms/common/list_node.py L23-L24, L58-L59 |
| end of list | boundary | `ListNode(7).next` | `None` | `None` | algorithms/common/list_node.py L27-L28 |
| end of list | interior | `values(ListNode(7, ListNode(8)))` | `[7, 8]` | `[7, 8]` | algorithms/common/list_node.py L27-L28 |
| truthiness | boundary | `bool(ListNode(0))` | `True` | `True` | algorithms/common/list_node.py L29-L30 |
| equality | equal | `ListNode(1, ListNode(2)) == ListNode(1, ListNode(2))` | `True` | `True` | algorithms/common/list_node.py L31-L34 |
| equality | length differs | `ListNode(1) == ListNode(1, ListNode(2))` | `False` | `False` | algorithms/common/list_node.py L31-L34 |
| equality | tail differs | `ListNode(1, ListNode(2)) == ListNode(1, ListNode(3))` | `False` | `False` | algorithms/common/list_node.py L31-L34 |
| equality | non-node | `ListNode(1) == 1` | `False` | `False` | algorithms/common/list_node.py L33-L34 |
| construction | no copy | `values after tail.val = 9` | `[1, 9]` | `[1, 9]` | algorithms/common/list_node.py L25-L26 |
| mutation | relink | `values after head.next = head.next.next` | `[1, 3]` | `[1, 3]` | algorithms/common/list_node.py L35 |
| repr | boundary | `repr(ListNode())` | `'ListNode(val=0, next=None)'` | `'ListNode(val=0, next=None)'` | algorithms/common/list_node.py L39, L54-L55 |
| repr | cycle | `repr of node whose next is itself` | `'ListNode(val=1, next=...)'` | `'ListNode(val=1, next=...)'` | algorithms/common/list_node.py L39 |
| hashing | boundary | `hash(ListNode())` | `'TypeError'` | `'TypeError'` | algorithms/common/list_node.py L36-L38 |

## Unsupported (documented, not tested, no new guards added)

| Input | Behavior | Source |
|---|---|---|
| val of a type other than int | stored as given, not validated | algorithms/common/list_node.py L42-L43, L58 |
| == or repr on very long lists | may raise RecursionError | algorithms/common/list_node.py L43-L46 |
| == between two different cyclic lists | may raise RecursionError | algorithms/common/list_node.py L45-L46 |
