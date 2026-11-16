# R24-T027 worked example for geometric_mean

Input `[2, 8, 4]` (the anchor `[2, 8]` plus one value).

| State | Hand-calculated | Traced execution | Result |
|---|---|---|---|
| product_states | `[1.0, 2.0, 16.0, 64.0]` | `[1.0, 2.0, 16.0, 64.0]` | PASS |
| n | `3` | `3` | PASS |
| result_rounded_to_4_places | `4.0` | `4.0` | PASS |

Decisive transition: the loop only accumulates a product (64.0); the return line `product ** (1 / n)` turns it into the n-th root. The raw traced result is `3.9999999999999996`. Floating-point roots can be off in the last digits, which is why the docstring examples round to 4 places.
