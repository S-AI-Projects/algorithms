"""Focused check for R24-T029: measure the work done by last_occurrence.

Run from the repository root:

    python3 work/R24-T029/check.py

Input size: n = len(array), the length of the sorted list searched.

Claim (worst case, from the code): each loop pass either returns or at least
halves the range still searched, so one search makes at most
floor(log2(n)) + 1 passes, which is ``n.bit_length()`` in Python. Each pass
reads at most 4 array elements, so at most 4 * n.bit_length() reads.

Experiment:
- Sizes 1,000, 10,000 and 100,000, with 5 repetitions per size. Every
  repetition builds a fresh sorted array from ``random.Random(24029)``: even
  values with about 4 copies each, so every odd value in range is absent.
- Each repetition runs 58 queries: 48 present values, 8 absent values inside
  the range, one below every element and one above every element (the worst
  case).
- Operation counts are the measure. Loop passes are counted with
  ``sys.settrace`` and element reads with a counting list; neither is timed.
- Timing is reported but never judged. ``perf_counter_ns`` covers only the
  calls, after a warm-up call per query. Process start-up, imports,
  compilation, array building, correctness checks and file I/O all happen
  outside the timed interval.

It exits non-zero if any of these fails:

1. The source anchors and the neighbouring inputs give their hand-calculated
   expected values.
2. Every measured search returns the same index as an independent answer
   from the standard library (``bisect.bisect_right``), checked outside the
   timed interval.
3. Every measured search stays within the claimed bounds on passes and
   reads.
4. The focused regression tests (``TestLastOccurrenceWork`` in
   ``tests/test_searching.py``), run with pytest using the project's pytest
   settings from ``pyproject.toml``. A run that collects zero tests counts as
   a failure.

No pass/fail rule depends on wall-clock speed.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, complexity.md and check_output.txt.
"""

from __future__ import annotations

import bisect
import importlib.metadata
import inspect
import json
import platform
import random
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test.
from algorithms.searching.last_occurrence import last_occurrence  # noqa: E402

TEST_NODE = "tests/test_searching.py::TestLastOccurrenceWork"
SEED = 24029
SIZES = [1_000, 10_000, 100_000]
REPETITIONS = 5
PRESENT_QUERIES = 48
ABSENT_INSIDE_QUERIES = 8
READS_PER_PASS = 4
LOOP_LINE_TEXT = "mid = (high + low) // 2"

# Expected values calculated by hand before running the source.
ANCHORS = [
    {"name": "anchor", "array": [1, 2, 2, 2, 3, 4], "query": 2, "expected": 3},
    {"name": "anchor", "array": [1, 2, 3, 4, 5], "query": 6, "expected": -1},
    {
        "name": "neighbour: one more 2",
        "array": [1, 2, 2, 2, 2, 3, 4],
        "query": 2,
        "expected": 4,
    },
    {
        "name": "neighbour: the final value",
        "array": [1, 2, 3, 4, 5],
        "query": 5,
        "expected": 4,
    },
]


class CountingList(list):
    """A list that counts how many elements are read from it."""

    def __init__(self, values):
        super().__init__(values)
        self.reads = 0

    def __getitem__(self, index):
        self.reads += 1
        return super().__getitem__(index)


def oracle(array: list[int], query: int) -> int:
    """Independent answer from the standard library, not a binary search copy."""
    index = bisect.bisect_right(array, query) - 1
    return index if index >= 0 and array[index] == query else -1


def safe(array: list[int], query: int) -> object:
    try:
        return last_occurrence(array, query)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"


def loop_line() -> int | None:
    source_lines, start = inspect.getsourcelines(last_occurrence)
    for offset, line in enumerate(source_lines):
        if line.strip() == LOOP_LINE_TEXT:
            return start + offset
    return None


def count_passes(array: list[int], query: int, line: int | None) -> int | None:
    """Count loop passes: how often the line computing mid runs."""
    if line is None:
        return None
    passes = 0
    code = last_occurrence.__code__

    def local_tracer(frame, event, arg):
        nonlocal passes
        if event == "line" and frame.f_lineno == line:
            passes += 1
        return local_tracer

    def global_tracer(frame, event, arg):
        if event == "call" and frame.f_code is code:
            return local_tracer
        return None

    previous = sys.gettrace()
    sys.settrace(global_tracer)
    try:
        safe(array, query)
    finally:
        sys.settrace(previous)
    return passes


def make_array(rng: random.Random, n: int) -> list[int]:
    """Sorted even values with about 4 copies each, so odd values are absent."""
    return sorted(2 * rng.randrange(n // 4) for _ in range(n))


def make_queries(rng: random.Random, array: list[int], n: int) -> list[int]:
    present = [rng.choice(array) for _ in range(PRESENT_QUERIES)]
    absent_inside = [
        2 * rng.randrange(n // 4 - 1) + 1 for _ in range(ABSENT_INSIDE_QUERIES)
    ]
    return present + absent_inside + [-1, array[-1] + 1]


def spread(values: list[float]) -> dict:
    return {
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
    }


def run_experiment(line: int | None) -> list[dict]:
    rng = random.Random(SEED)
    sizes = []
    for n in SIZES:
        bound_passes = n.bit_length()
        bound_reads = READS_PER_PASS * bound_passes
        repetitions = []
        for rep in range(REPETITIONS):
            array = make_array(rng, n)  # fresh input for every repetition
            queries = make_queries(rng, array, n)

            # Correctness, outside the timed interval.
            mismatches = []
            for query in queries:
                actual, expected = safe(array, query), oracle(array, query)
                if actual != expected:
                    mismatches.append(
                        {"query": query, "expected": expected, "actual": actual}
                    )

            # Operation counts, outside the timed interval.
            passes = [count_passes(array, query, line) for query in queries]
            counting = CountingList(array)
            reads = []
            for query in queries:
                counting.reads = 0
                safe(counting, query)
                reads.append(counting.reads)

            # Timing of the calls only, after a warm-up call per query.
            for query in queries:
                safe(array, query)
            start = time.perf_counter_ns()
            for query in queries:
                last_occurrence(array, query)
            elapsed = time.perf_counter_ns() - start

            within = all(p is not None and p <= bound_passes for p in passes) and all(
                r <= bound_reads for r in reads
            )
            repetitions.append(
                {
                    "repetition": rep + 1,
                    "queries": len(queries),
                    "mismatches": mismatches,
                    "max_passes": max(p if p is not None else -1 for p in passes),
                    "median_passes": statistics.median(
                        p if p is not None else -1 for p in passes
                    ),
                    "max_reads": max(reads),
                    "ns_per_call": elapsed / len(queries),
                    "within_bounds": within,
                    "passed": not mismatches and within,
                }
            )
        sizes.append(
            {
                "n": n,
                "bound_passes": bound_passes,
                "bound_reads": bound_reads,
                "repetitions": repetitions,
                "max_passes": spread([r["max_passes"] for r in repetitions]),
                "median_passes": spread([r["median_passes"] for r in repetitions]),
                "max_reads": spread([r["max_reads"] for r in repetitions]),
                "ns_per_call": spread([r["ns_per_call"] for r in repetitions]),
                "passed": all(r["passed"] for r in repetitions),
            }
        )
    return sizes


def run_anchors() -> list[dict]:
    results = []
    for case in ANCHORS:
        array = list(case["array"])
        actual = safe(array, case["query"])
        results.append(
            {
                **case,
                "actual": actual,
                "passed": actual == case["expected"] and array == case["array"],
            }
        )
    return results


def run_pytest() -> dict:
    command = [sys.executable, "-m", "pytest", TEST_NODE, "-q", "--no-header"]
    proc = subprocess.run(
        command, cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    output = proc.stdout + proc.stderr
    passed = re.search(r"(\d+) passed", output)
    failed = re.search(r"(\d+) failed", output)
    n_passed = int(passed.group(1)) if passed else 0
    n_failed = int(failed.group(1)) if failed else 0
    return {
        "command": "python3 -m pytest " + TEST_NODE + " -q --no-header",
        "returncode": proc.returncode,
        "passed": n_passed,
        "failed": n_failed,
        "ok": proc.returncode == 0 and n_passed > 0 and n_failed == 0,
        "output": output,
    }


def tool_versions() -> dict:
    def version(pkg: str) -> str:
        try:
            return importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            return "not installed"

    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pytest": version("pytest"),
    }


def fmt(stats: dict, digits: int = 0) -> str:
    return (
        f"{stats['median']:.{digits}f} "
        f"(range {stats['min']:.{digits}f}-{stats['max']:.{digits}f})"
    )


def complexity_markdown(sizes: list[dict]) -> str:
    lines = [
        "# R24-T029 work done by last_occurrence",
        "",
        "Input size: n = len(array).",
        "",
        "**Claim (worst case, from the code):** at most floor(log2(n)) + 1 "
        "loop passes per search (`n.bit_length()`), and at most 4 element "
        "reads per pass.",
        "",
        "**Observations** (seed 24029, 5 fresh arrays per size, 58 queries "
        "each; median and range over the 5 repetitions):",
        "",
        "| n | Claimed max passes | Observed max passes | Observed median "
        "passes | Observed max reads (bound) | Time per call, ns (not judged) |",
        "|---|---|---|---|---|---|",
    ]
    for s in sizes:
        lines.append(
            f"| {s['n']:,} | {s['bound_passes']} | {fmt(s['max_passes'])} "
            f"| {fmt(s['median_passes'], 1)} | {fmt(s['max_reads'])} "
            f"({s['bound_reads']}) | {fmt(s['ns_per_call'])} |"
        )
    lines += [
        "",
        "Each tenfold increase in n adds about log2(10) = 3.3 passes, which "
        "is the logarithmic growth the claim predicts. Timings cover only the "
        "calls (after a warm-up), not start-up, imports, compilation, input "
        "building, checking or I/O. They are dominated by per-call overhead, "
        "so the operation counts are the evidence.",
    ]
    return "\n".join(lines) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    line = loop_line()
    anchors = run_anchors()
    sizes = run_experiment(line)
    pytest_result = run_pytest()

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    out = ["R24-T029 last_occurrence work measurement", ""]
    out.append(f"Loop line counted for passes: L{line} {LOOP_LINE_TEXT!r}")
    out.append("")
    out.append("Anchors and neighbouring inputs (expected vs actual):")
    for r in anchors:
        out.append(
            f"  [{mark(r['passed'])}] {r['name']}: last_occurrence({r['array']}, "
            f"{r['query']}) expected={r['expected']} actual={r['actual']}"
        )
    out.append("")
    out.append(
        f"Experiment (seed {SEED}, {REPETITIONS} fresh arrays per size; "
        "median and range over repetitions):"
    )
    for s in sizes:
        mismatches = sum(len(r["mismatches"]) for r in s["repetitions"])
        queries = sum(r["queries"] for r in s["repetitions"])
        out.append(
            f"  [{mark(s['passed'])}] n={s['n']:,}: correct {queries - mismatches}/"
            f"{queries}; max passes {fmt(s['max_passes'])} <= {s['bound_passes']}; "
            f"median passes {fmt(s['median_passes'], 1)}; max reads "
            f"{fmt(s['max_reads'])} <= {s['bound_reads']}; time per call "
            f"{fmt(s['ns_per_call'])} ns (reported, not judged)"
        )
    out.append("")
    out.append(f"Pytest command: {pytest_result['command']}")
    out.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    out.append(pytest_result["output"].rstrip())

    overall = (
        line is not None
        and all(r["passed"] for r in anchors)
        and all(s["passed"] for s in sizes)
        and pytest_result["ok"]
    )
    out.append("")
    out.append("OVERALL: " + mark(overall))
    report = "\n".join(out) + "\n"

    write_json(
        "inputs.json",
        {
            "seed": SEED,
            "sizes": SIZES,
            "repetitions": REPETITIONS,
            "queries_per_repetition": {
                "present": PRESENT_QUERIES,
                "absent_inside_range": ABSENT_INSIDE_QUERIES,
                "below_every_element": 1,
                "above_every_element": 1,
            },
            "array_recipe": "sorted(2 * rng.randrange(n // 4) for _ in range(n))",
            "anchors_and_neighbours": ANCHORS,
        },
    )
    write_json("results.json", {"anchors": anchors, "sizes": sizes})
    write_json(
        "summary.json",
        {
            "task": "R24-T029",
            "target": "algorithms/searching/last_occurrence.py:last_occurrence",
            "input_size": "n = len(array)",
            "claim": "at most n.bit_length() loop passes and 4 reads per pass",
            "observed_max_passes": {s["n"]: s["max_passes"]["max"] for s in sizes},
            "bound_passes": {s["n"]: s["bound_passes"] for s in sizes},
            "all_correct_and_within_bounds": all(s["passed"] for s in sizes),
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "complexity.md").write_text(complexity_markdown(sizes), encoding="utf-8")
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
