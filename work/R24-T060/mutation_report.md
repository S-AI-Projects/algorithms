# Mutation-Resistant Regression Report (R24-T060)

Cited source: `algorithms/sorting/cocktail_shaker_sort.py`

## Invariants & Contract Checked
1. **Sorted Ascending Order**: Output satisfies $\forall i: \text{arr}[i] \le \text{arr}[i+1]$.
2. **Multiplicity Preservation**: Elements and counts are exactly preserved (tested with `[2, 2, 1]` $\to$ `[1, 2, 2]`).
3. **In-place Mutation**: Mutates and returns the exact same list instance (`res is arr`).
4. **Boundary collections**: Correctly handles empty `[]` and single-element `[1]` lists.

## Deliberate Mutant
- **Plausible mistake**: An off-by-one boundary error in the forward sweep:
  ```python
  # Original:
  for i in range(1, n):
  # Mutant:
  for i in range(1, n - 1):
  ```
- **Distinguishing Input**: `[1, 3, 2]`
  - On the forward pass, the mutant checks indices up to $n-2$ (comparing 1 and 3). Since $1 < 3$, no swap occurs and `swapped` remains `False`.
  - The mutant encounters `if not swapped: return array` and exits immediately, returning `[1, 3, 2]`.
  - **Original Output**: `[1, 2, 3]` (PASS).
  - **Mutant Output**: `[1, 3, 2]` (FAILS assertion `res == [1, 2, 3]`).
- **Conclusion**: The regression test uniquely and semantically detects this boundary mistake. The mutant is kept out of the production source.
