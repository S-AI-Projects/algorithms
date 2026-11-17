# R24-T012 boundary table for RandomListNode and copy_random_pointer

Source: algorithms/linked_list/copy_random_pointer.py at bd1d152.

| Partition | Case / Input | Expected | Source Contract | Result |
|---|---|---|---|---|
| valid boundary | `None` | None | copy_random_pointer.py L28-54; head is None returns None | PASS |
| valid boundary | `None` | None | copy_random_pointer.py L57-83; head is None returns None | PASS |
| valid boundary | `RandomListNode(1)` | distinct node with label=1, next=None, random=None | copy_random_pointer.py L19, L28; 1-node deep copy | PASS |
| valid boundary | `RandomListNode(1)` | distinct node with label=1, next=None, random=None | copy_random_pointer.py L19, L57; 1-node deep copy | PASS |
| valid boundary | `RandomListNode(1) with random=self` | distinct copy with copy.random is copy | copy_random_pointer.py L38-42; self-referential random pointer | PASS |
| valid boundary | `RandomListNode(1) with random=self` | distinct copy with copy.random is copy | copy_random_pointer.py L67-71; self-referential random pointer | PASS |
| valid boundary | `RandomListNode(0)` | label == 0 | RandomListNode L22-25; preserves label 0 | PASS |
| valid boundary | `RandomListNode(-7)` | label == -7 | RandomListNode L22-25; negative integer supported | PASS |
| valid interior | `RandomListNode('A')` | label == 'A' | RandomListNode L22-25; generic label assignment | PASS |
| explicitly unsupported | `RandomListNode()` | raises TypeError | RandomListNode.__init__(self, label: int) requires label argument | PASS |
