# R24-T014 Invariant Analysis for wiggle_sort

Source: `algorithms/sorting/wiggle_sort.py`

## Invariant Definition

1. **Wiggle Invariant**: For all indices `0 <= i < len(arr) - 1`:
   - When `i` is even: `arr[i] <= arr[i + 1]`
   - When `i` is odd:  `arr[i] >= arr[i + 1]`
   - Equivalently: `nums[0] <= nums[1] >= nums[2] <= nums[3] ...`

2. **Multiplicity Preservation**: Output is a permutation of input;
   `sorted(result) == sorted(input)`.

3. **In-place Mutation**: `result is input`.

## Broken Invariant Detection
- Broken sort detected: True
- Smallest counterexample: `[3, 1, 2]`
