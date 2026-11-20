# pancake_sort worked example (R24-T047)

A flip reverses a prefix. Each pass handles the unsorted prefix
`array[:cur]`. Decisive transition: after the pass for `cur`, the
prefix's largest value is at index `cur - 1` and is never moved again.

| Input | State after each flip (hand = traced) | Result |
|---|---|---|
| `[3, 1, 2]` | [2, 1, 3] → [1, 2, 3] | `[1, 2, 3]` |
| `[1, 3, 2]` | [3, 1, 2] → [2, 1, 3] → [1, 2, 3] | `[1, 2, 3]` |
| `[2, 2, 1]` | [1, 2, 2] | `[1, 2, 2]` |
| `[1, 2, 3]` | no flips | `[1, 2, 3]` |
| `[3, 2, 1]` | [1, 2, 3] | `[1, 2, 3]` |
| `[]` | no flips | `[]` |
| `[5]` | no flips | `[5]` |
