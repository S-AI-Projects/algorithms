# R24-T023 findings

## find_min_rotate (task target)

Matches the independent oracle on 28 of 28 inputs (every rotation of sorted, duplicate-free lists of length 1-7). Repeated runs on fresh copies agree and no input is modified. No mismatch was found, so its code is unchanged.

## find_min_rotate_recur (sibling function, used as an anchor only)

Known defect: documented here, not fixed in this task (agreed scope).

- The anchor `find_min_rotate_recur([4, 5, 6, 7, 0, 1, 2], 0, 6)` returns 0 as documented.
- On the same 28 inputs it returns the wrong value for 11.
- Smallest failing input found: `[12, 9]` returns 12, expected 9.
- Minimal reproducible case: `find_min_rotate_recur([2, 1], 0, 1)` returns 2; expected 1.
- Cause: the base case `if mid == low: return array[low]` (L59-60 at bd1d152) stops as soon as the range holds two items, without comparing `array[low]` with `array[high]`. When the minimum is at `high`, it is missed.
- A minimal fix would stop when `low == high` instead. Not applied here.
