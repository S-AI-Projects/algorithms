# Failure Path Coverage for `multiply` (R24-T058)

Cited source: `algorithms/matrix/matrix_exponentiation.py`

## Covered Scenarios
1. **1×1 Matrix Fixture**:
   - Input: `[[3]], [[4]]` -> Output: `[[12]]`.
2. **Zero-Containing Matrix Fixture**:
   - Input: `[[0, 2], [3, 0]], [[1, 0], [0, 4]]` -> Output: `[[0, 8], [3, 0]]`.
3. **Empty / Absent-Result Boundary**:
   - Total contract path: `multiply([], [])` evaluates with `size = 0` and returns `[]`.
4. **Failure Path (Incompatible Rectangular Matrices)**:
   - Input: 2×1 column matrices `a = [[1], [2]]`, `b = [[3], [4]]`.
   - Reached branch: Innermost loop `result[i][j] += mat_a[i][k] * mat_b[k][j]` at line 46 raises `IndexError: list index out of range` because `mat_a[0]` has length 1 when `k=1`.
   - Caller state preservation: Both `a` and `b` remain completely unchanged.
   - Subsequent call: `multiply([[1, 0], [0, 1]], [[2, 3], [4, 5]])` succeeds immediately afterwards, confirming zero residual state corruption.
