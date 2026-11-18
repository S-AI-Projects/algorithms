# Executable Worked Example & Trace of `trimmean` (R24-T057)

Cited source: `algorithms/array/trimmean.py`

## Decisive State Transition
The core calculation of `trimmean(array, percentage)` proceeds through the following concrete steps:
1. **Ratio calculation**: `ratio = percentage / 200` represents the tail trimming fraction.
2. **In-place ordering**: `array.sort()` mutates the list into ascending order.
3. **Decisive trim count calculation**: `trim_count = int(len(array) * ratio)`.
4. **Subarray selection**: `trimmed = array[trim_count : len(array) - trim_count]`.
5. **Arithmetic mean**: Sum of elements in `trimmed` divided by `len(trimmed)`.

## Traced Execution Matrix
| Stage | Expression / Operation | State for `([10.0, 2.0, 4.0, 8.0, 6.0], 40)` |
|---|---|---|
| Input | Raw array & trim % | `array = [10.0, 2.0, 4.0, 8.0, 6.0]`, `percentage = 40` |
| Sort | `array.sort()` | `array = [2.0, 4.0, 6.0, 8.0, 10.0]` |
| Ratio | `40 / 200` | `0.20` |
| Trim count | `int(5 * 0.20)` | `1` element from each end |
| Slicing | `array[1 : 4]` | `[4.0, 6.0, 8.0]` |
| Sum | `4.0 + 6.0 + 8.0` | `18.0` |
| Result | `18.0 / 3` | `6.0` |
