# Supported Boundaries of `planting_trees` (R24-T052)

Cited source: `algorithms/dynamic_programming/planting_trees.py`

| Domain Category | Input (`trees`, `length`, `width`) | Expected Result | Actual Result | Notes / Contract |
|---|---|---|---|---|
| **Anchor (Interior)** | `[0, 1, 10, 10], 10, 1` | `2.414213562373095` | `2.414213562373095` | Executable source anchor from docstring |
| **Neighbor (Interior)** | `[0, 0, 10, 10], 10, 1` | `2.0` | `2.0` | Trees already at optimal endpoints; only width costs apply |
| **Boundary (width=0)** | `[0, 0, 10, 10], 10, 0` | `0.0` | `0.0` | Valid boundary at width=0 (cross-road displacement penalty is 0) |
| **Boundary (length=0, width=0)** | `[0, 0, 0, 0], 0, 0` | `0.0` | `0.0` | Valid boundary: zero-length road and zero-width road |
| **Boundary (smallest N=4)** | `[1, 2, 3, 4], 3, 0` | `4.0` | `4.0` | Smallest supported collection (N=4, 2 pairs) |
| **Immutability Contract** | `[0, 1, 10, 10], 10, 1` | `trees` unchanged | `trees` unchanged | Pure function; input list is never modified in place |
| **Unsupported Boundary** | `[1, 2], 10, 1` | `ZeroDivisionError` | `ZeroDivisionError` | N < 4 leads to n_pairs <= 1, causing division by zero in spacing calculation |
