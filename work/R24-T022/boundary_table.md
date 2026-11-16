# R24-T022 boundary table for first_switch_pairs

Source: algorithms/stack/switch_pairs.py at bd1d152. The stack is read
bottom to top (L24): index 0 is the bottom, the last item is the top.

| Partition | Input | Expected | Actual | Same list | Source | Result |
|---|---|---|---|---|---|---|
| valid boundary | `[]` | `[]` | `[]` | True | L34/L36 loops run zero times; L44 returns stack | PASS |
| valid boundary | `[7]` | `[7]` | `[7]` | True | L5; odd case L38-40 | PASS |
| valid boundary | `[1, 2]` | `[2, 1]` | `[2, 1]` | True | L4; swap L41-43 | PASS |
| valid boundary | `[1, 2, 3]` | `[2, 1, 3]` | `[2, 1, 3]` | True | L5; odd case L38-40 | PASS |
| valid interior | `[1, 2, 3, 4]` | `[2, 1, 4, 3]` | `[2, 1, 4, 3]` | True | L4 | PASS |
| valid interior | `[3, 8, 17, 9, 1, 10]` | `[8, 3, 9, 17, 10, 1]` | `[8, 3, 9, 17, 10, 1]` | True | L30-31 (existing doctest) | PASS |
| unsupported | a tuple or None | undefined | not executed | n/a | L33-44, no guard | n/a |

Fixture: push A, B, C; pop twice; push D; drain. Expected pop order ['C', 'B', 'D', 'A'], actual ['C', 'B', 'D', 'A'].

| After | Stack | first_switch_pairs(copy) expected | Actual | Result |
|---|---|---|---|---|
| push A, B, C | `['A', 'B', 'C']` | `['B', 'A', 'C']` | `['B', 'A', 'C']` | PASS |
| pop twice | `['A']` | `['A']` | `['A']` | PASS |
| push D | `['A', 'D']` | `['D', 'A']` | `['D', 'A']` | PASS |
| drain | `[]` | `[]` | `[]` | PASS |

Unsupported note: No guard in the source (L33-44) and no documented exception, so behaviour is undefined and no exception is asserted.
