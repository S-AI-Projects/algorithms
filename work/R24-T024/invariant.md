# R24-T024 invariant of Node (add_two_numbers.py)

## Invariant

- `Node(x)` stores `x` in `val` and starts with `next` set to `None`, so one node is the smallest supported list.
- Following `next` from the head of a list of distinct linked nodes visits each node exactly once and stops at `None`.
- Ownership: the module's functions only read the nodes they are given and return lists built from new nodes.

## Why it holds (source at bd1d152)

- L19-21: `__init__` sets `val` and `next = None`; there is no other method, so a node only changes when a caller assigns to it.
- L44-51: `add_two_numbers` only reads `left`/`right` (`.val`, `.next`) and moves its local variables along the lists.
- L52, L55: every sum digit is a new `Node(...)`, linked in order, so the sum shares no node with its inputs and has no cycle.
- L102-106: `convert_to_str` only reads `val` and follows `next`.

## Generator domain

The module docstring (L4-6) defines the domain as non-empty lists of digits for non-negative integers, least significant digit first. The generator draws non-negative integers with 1-12 digits from `random.Random(24024)` and turns each into its digits. That gives no empty lists, no leading zeros and only digits 0-9.

## Result

- Fixtures: 18/18 checks passed.
- Property cases: 203/203 passed (3 readable + 200 seeded).
- Readable small case kept for review: 342 + 465 is 2->4->3 plus 5->6->4, giving 7->0->8 from three new nodes.
