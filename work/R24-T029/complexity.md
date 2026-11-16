# R24-T029 work done by last_occurrence

Input size: n = len(array).

**Claim (worst case, from the code):** at most floor(log2(n)) + 1 loop passes per search (`n.bit_length()`), and at most 4 element reads per pass.

**Observations** (seed 24029, 5 fresh arrays per size, 58 queries each; median and range over the 5 repetitions):

| n | Claimed max passes | Observed max passes | Observed median passes | Observed max reads (bound) | Time per call, ns (not judged) |
|---|---|---|---|---|---|
| 1,000 | 10 | 10 (range 10-10) | 10.0 (range 9.0-10.0) | 32 (range 32-32) (40) | 569 (range 524-593) |
| 10,000 | 14 | 14 (range 14-14) | 13.0 (range 13.0-13.0) | 45 (range 45-46) (56) | 836 (range 784-894) |
| 100,000 | 17 | 17 (range 17-17) | 16.0 (range 16.0-16.5) | 54 (range 54-54) (68) | 988 (range 976-1035) |

Each tenfold increase in n adds about log2(10) = 3.3 passes, which is the logarithmic growth the claim predicts. Timings cover only the calls (after a warm-up), not start-up, imports, compilation, input building, checking or I/O. They are dominated by per-call overhead, so the operation counts are the evidence.
