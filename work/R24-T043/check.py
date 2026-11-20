#!/usr/bin/env python3
"""Focused check runner for R24-T043: distance_between_two_points vs a reference.

1. Compares the function with a reviewed result table (values worked out by
   hand, including the source anchors and one neighbouring input).
2. Compares it with an independent oracle on every integer input in
   -2..2 (625 inputs). The oracle builds the exact squared distance as an
   int and takes a 50-digit Decimal square root; it never calls the
   function under test.
3. Checks repeated runs with fresh equivalent inputs give the same result.
4. Records the documented out-of-domain mismatches (overflow and underflow)
   with minimal reproducing inputs. These are reported, not counted as
   failures, because the docstring lists them as limits.
5. Runs the focused pytest class with the project's pytest configuration:
   tests/test_math.py::TestDistanceBetweenTwoPoints

Writes evidence to work/R24-T043/ and exits non-zero if any check fails.
The function has no external I/O, so nothing needs mocking.

Usage:
    python3 work/R24-T043/check.py
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from decimal import Decimal, localcontext
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T043"
sys.path.insert(0, str(ROOT))

from algorithms.math.distance_between_two_points import (  # noqa: E402
    distance_between_two_points,
)

PYTEST_TARGET = "tests/test_math.py::TestDistanceBetweenTwoPoints"

# Reviewed result table: (x1, y1, x2, y2), expected, how it was derived.
TABLE = [
    ((0, 0, 3, 4), 5.0, "anchor: dx=3, dy=4, sqrt(25)"),
    ((-1, -1, 2, 3), 5.0, "anchor: dx=3, dy=4, sqrt(25)"),
    ((-1, -1, 2, 4), 5.830951894845301, "neighbor: dx=3, dy=5, sqrt(34)"),
    ((0, 0, 5, 12), 13.0, "dx=5, dy=12, sqrt(169)"),
    ((1, 1, 9, 16), 17.0, "dx=8, dy=15, sqrt(289)"),
    ((0, 0, 0, 0), 0.0, "same point"),
    ((-4, 2, 3, 2), 7.0, "horizontal only, |dx|=7"),
    ((5, -3, 5, 6), 9.0, "vertical only, |dy|=9"),
    ((0, 0, 1, 1), 1.4142135623730951, "sqrt(2)"),
    ((0.5, 0.5, 3.5, 4.5), 5.0, "dx=3.0, dy=4.0 exactly"),
    ((10, -7, 13, -3), 5.0, "anchor shifted by (+10, -7)"),
]

# Out-of-domain inputs documented in the docstring "Limits" section.
KNOWN_LIMITS = [
    ((0, 0, 1e200, 0), "1e200", "dx ** 2 overflows the float range"),
    ((0, 0, 1e-200, 0), "1e-200", "dx ** 2 underflows to 0.0"),
]


def reference_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
    with localcontext() as ctx:
        ctx.prec = 50
        return float(Decimal(squared).sqrt())


def tool_versions() -> dict[str, str]:
    versions = {"python": platform.python_version(), "platform": platform.platform()}
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

    log("R24-T043: distance_between_two_points reference comparison")

    table_results = []
    for args, expected, why in TABLE:
        actual = distance_between_two_points(*args)
        ok = actual == expected
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [table] {args} expected={expected!r} "
            f"actual={actual!r} ({why})"
        )
        table_results.append(
            {
                "args": list(args),
                "expected": expected,
                "actual": actual,
                "derivation": why,
                "passed": ok,
            }
        )

    grid_results = []
    grid_failures = 0
    for args in product(range(-2, 3), repeat=4):
        expected = reference_distance(*args)
        actual = distance_between_two_points(*args)
        ok = actual == expected
        grid_failures += not ok
        grid_results.append([list(args), expected, actual, ok])
        if not ok:
            log(f"FAIL [grid] {args} expected={expected!r} actual={actual!r}")
    failures += grid_failures
    log(
        f"{'PASS' if grid_failures == 0 else 'FAIL'} [grid] {len(grid_results)} "
        f"integer inputs in -2..2 vs Decimal oracle, {grid_failures} mismatches"
    )

    repeats = {distance_between_two_points(-1, -1, 2, 3) for _ in range(5)}
    repeats.add(distance_between_two_points(-1.0, -1.0, 2.0, 3.0))
    ok = repeats == {5.0}
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [repeat] 5 int runs + 1 float run "
        f"expected={{5.0}} actual={sorted(repeats)}"
    )

    limit_results = []
    for args, true_value, cause in KNOWN_LIMITS:
        try:
            actual = repr(distance_between_two_points(*args))
        except OverflowError as exc:
            actual = f"OverflowError: {exc}"
        log(
            f"INFO [documented limit] {args} true distance={true_value} "
            f"actual={actual} ({cause})"
        )
        limit_results.append(
            {
                "args": [repr(v) for v in args],
                "true_distance": true_value,
                "actual": actual,
                "cause": cause,
            }
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
                "table": [
                    {"args": list(a), "expected": e, "derivation": w}
                    for a, e, w in TABLE
                ],
                "grid": "all (x1, y1, x2, y2) with each value in range(-2, 3)",
                "oracle": "float(Decimal(dx**2 + dy**2).sqrt()) at 50 digits",
                "known_limits": [
                    {"args": [repr(v) for v in a], "true_distance": t}
                    for a, t, _ in KNOWN_LIMITS
                ],
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "table": table_results,
                "grid": {
                    "count": len(grid_results),
                    "mismatches": grid_failures,
                    "rows": "[args, expected, actual, passed]",
                    "results": grid_results,
                },
                "repeat": {"expected": [5.0], "actual": sorted(repeats)},
                "known_limits": limit_results,
                "pytest": {
                    "command": f"python3 -m pytest {PYTEST_TARGET}",
                    "exit_code": proc.returncode,
                    "passed": passed,
                },
                "failures": failures,
            },
            indent=1,
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
