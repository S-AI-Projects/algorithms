#!/usr/bin/env python3
"""Focused check runner for R24-T041: contract of max_profit_naive.

1. Calls max_profit_naive directly on each fixture and compares it with an
   expected value derived by hand (not from running the source).
2. Confirms the input list is not mutated.
3. Runs the focused pytest class with the project's pytest configuration:
   tests/test_dynamic_programming.py::TestMaxProfitNaiveContract

Writes evidence to work/R24-T041/ and exits non-zero if any check fails.
The module has no external I/O, so nothing needs mocking.

Usage:
    python3 work/R24-T041/check.py
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T041"
sys.path.insert(0, str(ROOT))

from algorithms.dynamic_programming.buy_sell_stock import (  # noqa: E402
    max_profit_naive,
    max_profit_optimized,
)

PYTEST_TARGET = "tests/test_dynamic_programming.py::TestMaxProfitNaiveContract"

# (label, prices, expected, how the expected value was derived)
CASES = [
    ("anchor", [7, 1, 5, 3, 6, 4], 5, "buy 1, sell 6"),
    ("anchor", [7, 6, 4, 3, 1], 0, "strictly decreasing, no profit"),
    ("neighbor", [7, 1, 5, 3, 6, 4, 8], 7, "anchor + 8: buy 1, sell 8"),
    ("smallest", [], 0, "no days, no trade"),
    ("smallest", [5], 0, "one day, no trade"),
    ("two-day", [1, 2], 1, "buy 1, sell 2"),
    ("two-day", [2, 1], 0, "price falls"),
    ("repeated", [3, 3, 3, 3], 0, "equal prices give 0"),
    ("repeated", [2, 2, 5, 5, 2], 3, "buy 2, sell 5"),
]


def tool_versions() -> dict[str, str]:
    versions = {"python": platform.python_version(), "platform": platform.platform()}
    for pkg in ("pytest",):
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "not installed"
    return versions


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    failures = 0

    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    log("R24-T041: max_profit_naive contract checks")

    results = []
    for label, prices, expected, why in CASES:
        actual = max_profit_naive(list(prices))
        ok = actual == expected
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [{label}] {prices} expected={expected} "
            f"actual={actual}"
        )
        results.append(
            {
                "label": label,
                "prices": prices,
                "expected": expected,
                "actual": actual,
                "derivation": why,
                "passed": ok,
            }
        )

    # Source anchor for the optimized variant.
    anchor = [7, 1, 5, 3, 6, 4]
    opt = max_profit_optimized(anchor)
    ok = opt == 5
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [anchor] max_profit_optimized({anchor}) "
        f"expected=5 actual={opt}"
    )

    # Mutation behaviour, checked separately from return values.
    prices = [7, 1, 5, 3, 6, 4]
    snapshot = list(prices)
    max_profit_naive(prices)
    ok = prices == snapshot
    failures += not ok
    log(f"{'PASS' if ok else 'FAIL'} [mutation] input unchanged: {prices}")

    # Focused pytest run with the project's configuration.
    cmd = [sys.executable, "-m", "pytest", PYTEST_TARGET]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    match = re.search(r"(\d+) passed", proc.stdout)
    passed = int(match.group(1)) if match else 0
    ok = proc.returncode == 0 and passed > 0
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [pytest] {' '.join(cmd[1:])} -> "
        f"exit={proc.returncode}, {passed} passed"
    )
    if not ok:
        log(proc.stdout[-2000:] + proc.stderr[-2000:])

    log(f"RESULT: {'OK' if failures == 0 else f'{failures} FAILED'}")

    (WORK / "inputs.json").write_text(
        json.dumps(
            [
                {"label": c[0], "prices": c[1], "expected": c[2], "derivation": c[3]}
                for c in CASES
            ],
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "cases": results,
                "pytest": {
                    "command": "python3 -m pytest " + PYTEST_TARGET,
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
