#!/usr/bin/env python3
"""Focused check runner for R24-T049: measure the work done by tsp.

Input size: n = number of cities (rows of the n x n distance matrix).

1. Correctness fixture: source anchor (80), a neighbouring input with edge
   0-2 lowered to 5 (70, worked out by hand), 1 city, 2 cities, empty.
2. Operation count (deterministic, the pass/fail measure): every
   ``dist[pos][city]`` lookup is counted with a row type that counts
   ``__getitem__``. The count must equal the exact value predicted from
   the reachable DP states, for n = 1..14.
3. Timing (observation only, no pass/fail threshold): sizes n = 8, 11, 14,
   five repetitions each, a fresh seeded matrix per repetition. Only the
   tsp call is inside the timed interval (time.perf_counter); process
   startup, imports, input generation and correctness checks are outside
   it, and one warm-up call runs first. CPython has no JIT, so there is no
   compilation step to separate. Median and range are reported.
4. Every timed result is checked, outside the timed interval, against an
   independent bottom-up Held-Karp oracle, itself cross-checked by brute
   force for n = 8.
5. The focused pytest class with the project's pytest configuration:
   tests/test_dynamic_programming.py::TestTspBitmask

Writes evidence to work/R24-T049/ and exits non-zero if any correctness or
operation-count check fails. tsp has no external I/O, so nothing needs
mocking.

Usage:
    python3 work/R24-T049/check.py
"""

from __future__ import annotations

import importlib.metadata
import itertools
import json
import math
import platform
import random
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T049"
sys.path.insert(0, str(ROOT))

from algorithms.dynamic_programming.bitmask import tsp  # noqa: E402

PYTEST_TARGET = "tests/test_dynamic_programming.py::TestTspBitmask"
SEED = 49
COUNT_SIZES = range(1, 15)
TIMING_SIZES = (8, 11, 14)
REPETITIONS = 5

ANCHOR = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
NEIGHBOR = [[0, 10, 5, 20], [10, 0, 35, 25], [5, 35, 0, 30], [20, 25, 30, 0]]


class BudgetExceededError(Exception):
    """Raised when tsp reads far more entries than the prediction allows."""


class CountingRow(list):
    """A matrix row that counts reads; shared counter on the class.

    The budget stops a run that does far more work than predicted (for
    example with memoization removed, which is factorial time) so the
    check fails quickly instead of hanging.
    """

    reads = 0
    budget = math.inf

    def __getitem__(self, index):
        CountingRow.reads += 1
        if CountingRow.reads > CountingRow.budget:
            raise BudgetExceededError
        return super().__getitem__(index)


def random_matrix(n: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    return [[0 if i == j else rng.randint(1, 99) for j in range(n)] for i in range(n)]


def predicted_lookups(n: int) -> int:
    """Exact dist[pos][city] reads for tsp on n cities.

    Reachable memoized states (mask, pos) with k cities visited: 1 for
    k = 1 (only city 0), C(n-1, k-1) * (k-1) for 2 <= k <= n-1. Each reads
    one entry per unvisited city (n - k), and each state with k = n - 1
    triggers one base case that reads dist[pos][0].
    """
    if n == 1:
        return 1
    states = {
        k: 1 if k == 1 else math.comb(n - 1, k - 1) * (k - 1) for k in range(1, n)
    }
    return sum(count * (n - k) for k, count in states.items()) + states[n - 1]


def held_karp_oracle(dist: list[list[int]]) -> float:
    """Independent bottom-up Held-Karp: best[mask][j] = cheapest path from 0
    through the cities in mask, ending at j."""
    n = len(dist)
    if n == 0:
        return math.inf
    if n == 1:
        return dist[0][0]
    full = 1 << n
    best = [[math.inf] * n for _ in range(full)]
    best[1][0] = 0
    for mask in range(1, full, 2):
        for j in range(n):
            cost = best[mask][j]
            if cost == math.inf:
                continue
            for k in range(1, n):
                if not mask & (1 << k):
                    new = mask | (1 << k)
                    best[new][k] = min(best[new][k], cost + dist[j][k])
    return min(best[full - 1][j] + dist[j][0] for j in range(1, n))


def brute_force(dist: list[list[int]]) -> float:
    n = len(dist)
    return min(
        sum(dist[a][b] for a, b in itertools.pairwise((0, *order, 0)))
        for order in itertools.permutations(range(1, n))
    )


def tool_versions() -> dict[str, str]:
    versions = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.machine(),
    }
    try:
        versions["pytest"] = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        versions["pytest"] = "not installed"
    return versions


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    failures = 0

    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    log("R24-T049: tsp work measurement (n = number of cities)")

    fixture = [
        ("anchor (source doctest)", ANCHOR, 80),
        ("neighbor: edge 0-2 lowered 15 -> 5", NEIGHBOR, 70),
        ("1 city", [[0]], 0),
        ("2 cities: 0 -> 1 -> 0", [[0, 3], [4, 0]], 7),
        ("empty matrix", [], math.inf),
    ]
    fixture_results = []
    for label, dist, expected in fixture:
        actual = tsp(dist)
        ok = actual == expected
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [fixture] {label}: expected={expected} "
            f"actual={actual}"
        )
        fixture_results.append(
            {"case": label, "expected": str(expected), "actual": str(actual)}
        )

    count_results = []
    count_failures = 0
    for n in COUNT_SIZES:
        dist = random_matrix(n, SEED + n)
        expected = predicted_lookups(n)
        CountingRow.reads = 0
        CountingRow.budget = 10 * expected
        try:
            result = tsp([CountingRow(row) for row in dist])
        except BudgetExceededError:
            result = None
        CountingRow.budget = math.inf
        measured = CountingRow.reads
        correct = result == held_karp_oracle(dist)
        count_failures += not (measured == expected and correct)
        ok = measured == expected and correct
        failures += not ok
        bound = n * n * 2**n
        log(
            f"{'PASS' if ok else 'FAIL'} [ops] n={n:2d}: lookups expected="
            f"{expected} actual={measured}, ratio to n^2*2^n={measured / bound:.4f}, "
            f"result matches oracle={correct}"
        )
        count_results.append(
            {
                "n": n,
                "predicted_lookups": expected,
                "measured_lookups": measured,
                "n2_2n": bound,
                "ratio": round(measured / bound, 6),
                "result": result,
                "oracle_agrees": correct,
            }
        )

    timing_results = []
    if count_failures:
        failures += 1
        log("FAIL [timing] skipped: operation counts differ from the prediction")
    else:
        tsp(random_matrix(8, SEED))  # warm-up, not timed
    for n in TIMING_SIZES if not count_failures else ():
        times_ms = []
        for rep in range(REPETITIONS):
            dist = random_matrix(n, SEED * 1000 + n * 10 + rep)  # fresh input
            start = time.perf_counter()
            result = tsp(dist)
            elapsed = (time.perf_counter() - start) * 1000
            times_ms.append(elapsed)
            expected = held_karp_oracle(dist)  # checked outside the timing
            ok = result == expected
            if n == 8:
                ok = ok and expected == brute_force(dist)
            failures += not ok
            if not ok:
                log(
                    f"FAIL [timing] n={n} rep={rep}: expected={expected} "
                    f"actual={result}"
                )
        median = statistics.median(times_ms)
        log(
            f"INFO [timing] n={n:2d}: median {median:.2f} ms, range "
            f"{min(times_ms):.2f}-{max(times_ms):.2f} ms over {REPETITIONS} "
            f"fresh inputs; all {REPETITIONS} results correct"
        )
        timing_results.append(
            {
                "n": n,
                "times_ms": [round(t, 4) for t in times_ms],
                "median_ms": round(median, 4),
                "min_ms": round(min(times_ms), 4),
                "max_ms": round(max(times_ms), 4),
                "predicted_lookups": predicted_lookups(n),
            }
        )
    for prev, cur in itertools.pairwise(timing_results):
        log(
            f"INFO [growth] n {prev['n']} -> {cur['n']}: median time x"
            f"{cur['median_ms'] / prev['median_ms']:.1f}, lookups x"
            f"{cur['predicted_lookups'] / prev['predicted_lookups']:.1f}"
        )

    cmd = [sys.executable, "-m", "pytest", PYTEST_TARGET]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    match = re.search(r"(\d+) passed", proc.stdout)
    passed = int(match.group(1)) if match else 0
    ok = proc.returncode == 0 and passed > 0
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [pytest] python3 -m pytest {PYTEST_TARGET} "
        f"-> exit={proc.returncode}, {passed} passed"
    )
    if not ok:
        log(proc.stdout[-2000:] + proc.stderr[-2000:])

    log(f"RESULT: {'OK' if failures == 0 else f'{failures} FAILED'}")

    (WORK / "inputs.json").write_text(
        json.dumps(
            {
                "size_variable": "n = number of cities",
                "fixture": [
                    {"case": label, "dist": dist, "expected": str(expected)}
                    for label, dist, expected in fixture
                ],
                "op_count_matrices": "random_matrix(n, 49 + n), n = 1..14",
                "timing_matrices": "random_matrix(n, 49000 + 10 * n + rep)",
                "timing_sizes": list(TIMING_SIZES),
                "repetitions": REPETITIONS,
                "entries": "0 on the diagonal, random.randint(1, 99) elsewhere",
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "fixture": fixture_results,
                "operation_counts": count_results,
                "timing": timing_results,
                "pytest": {
                    "command": f"python3 -m pytest {PYTEST_TARGET}",
                    "exit_code": proc.returncode,
                    "passed": passed,
                },
                "failures": failures,
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "tool_versions.json").write_text(
        json.dumps(tool_versions(), indent=2) + "\n"
    )
    (WORK / "check_output.txt").write_text("\n".join(lines) + "\n")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
