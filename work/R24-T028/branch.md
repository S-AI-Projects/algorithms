# R24-T028 branch covered in matrix_chain_order

There is no error branch, so the covered path is the valid empty result: with at most one matrix (`len(array) <= 2`) the loop over chain lengths does not run, and the zero tables from L37-38 are returned at L51.

| Statement | Line at bd1d152 | Line on this branch |
|---|---|---|
| `for chain_length in range(2, n):` | L39 | L48 |
| `for a in range(1, n - chain_length + 1):` | L40 | L49 |
| `return matrix, sol` | L51 | L60 |

| Input | Loop header ran | Loop body ran | Returned | Result |
|---|---|---|---|---|
| `[2, 3]` (2 x 3 rectangular matrix) | True | False | True | PASS |
| `[1, 1]` (1 x 1 matrix) | True | False | True | PASS |
| `[0, 3]` (0 x 3 zero-dimension matrix) | True | False | True | PASS |
| `[]` (smallest input []) | True | False | True | PASS |
| `[5]` (one dimension [5]) | True | False | True | PASS |
