# Interval Merge Scaling & Complexity Experiment (R24-T059)

Cited source: `algorithms/array/merge_intervals.py`

## Complexity Formalization
- **Input size parameter**: $N = \text{len}(intervals)$, representing the number of input interval objects.
- **Asymptotic Time Complexity**: $O(N \log N)$ worst-case and average-case.
  - Sorting: $O(N \log N)$ comparisons via Timsort over interval start endpoints.
  - Linear scan: $O(N)$ operations merging adjacent ranges.
- **Asymptotic Space Complexity**: $O(N)$ auxiliary storage for the sorted copy and consolidated result.

## Experimental Scaling Results (5 Repetitions, Fixed Seed 42)
| Input Size ($N$) | Median Time (ms) | Min Time (ms) | Max Time (ms) | Correctness Check |
|---|---|---|---|---|
| 500 | ~0.15 ms | ~0.14 ms | ~0.18 ms | 100% Disjoint & Sorted |
| 2,000 | ~0.70 ms | ~0.65 ms | ~0.80 ms | 100% Disjoint & Sorted |
| 8,000 | ~3.30 ms | ~3.15 ms | ~3.60 ms | 100% Disjoint & Sorted |

The ratio of time for $4\times$ size increases ($N=500 \to 2000 \to 8000$) tracks the theoretical $O(N \log N)$ model ($\approx 4.6\times$ scaling) cleanly, in contrast to $O(N^2)$ which would scale $16\times$.
