# Invariants and Property Tests of `josephus` (R24-T054)

Cited source: `algorithms/array/josephus.py`

## Invariants Formulated and Proven
1. **Permutation & Conservation Invariant**:
   For any non-empty list of unique elements `items` and elimination step `skip >= 1`, the yielded sequence `R` is a valid permutation of `items`:
   - `len(R) == len(items)`
   - `sorted(R) == sorted(items)`
   - Every element is eliminated exactly once.

2. **Survivor Recurrence Invariant**:
   For $n$ participants labeled $1 \dots n$ and skip $k$, the last eliminated person (the survivor) strictly matches the standard closed-form recurrence:
   $$J(1, k) = 0$$
   $$J(i, k) = (J(i - 1, k) + k) \pmod i \quad \text{for } 2 \le i \le n$$
   Expected survivor is `original[J(n, k)]`.

3. **Identity Property ($k = 1$)**:
   When `skip = 1`, people are eliminated strictly in sequential order:
   `list(josephus(items, 1)) == items`.

4. **In-place Mutation Contract**:
   The input list is consumed in-place by `items.pop(index)`; when the generator finishes, `len(items) == 0`.

## Anchor and Neighboring Fixtures
- Anchor: `list(josephus([1, 2, 3, 4, 5, 6, 7, 8, 9], 3))` -> `[3, 6, 9, 4, 8, 5, 2, 7, 1]`
- Neighbor: `list(josephus([1, 2, 3, 4, 5, 6, 7, 8, 9], 2))` -> `[2, 4, 6, 8, 1, 5, 9, 7, 3]`
- 100 bounded valid inputs evaluated with fixed seed `42`.
