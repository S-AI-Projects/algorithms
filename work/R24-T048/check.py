#!/usr/bin/env python3
"""Focused check runner for R24-T048: failure path of fizzbuzz.

Branch under test: the guard ``if number < 1`` in fizzbuzz
(algorithms/string/fizzbuzz.py), which raises
``ValueError("n cannot be less than one")``. Line numbers are looked up in
the source at run time and compared with the traceback, so each failing
input is shown to reach that exact line.

Checks:
1. Source anchors fizzbuzz(5) and fizzbuzz_with_helper_func(3), and the
   neighbouring inputs fizzbuzz(6) and fizzbuzz_with_helper_func(4).
2. fizzbuzz(0), the smallest input reaching the ValueError branch; -2 too.
3. fizzbuzz(None): TypeError raised by the ``number < 1`` comparison, so the
   later ``number is None`` check is never reached.
4. A valid call succeeds after the failure and earlier results are intact.
5. fizzbuzz_with_helper_func has no guard: inputs below 1 give [].
6. The focused pytest class with the project's pytest configuration:
   tests/test_string.py::TestFizzbuzzFailurePath

Writes evidence to work/R24-T048/ and exits non-zero if any check fails.
fizzbuzz has no external I/O, so nothing needs mocking.

Usage:
    python3 work/R24-T048/check.py
"""

from __future__ import annotations

import importlib
import importlib.metadata
import inspect
import json
import platform
import re
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T048"
sys.path.insert(0, str(ROOT))

MODULE = importlib.import_module("algorithms.string.fizzbuzz")
fizzbuzz = MODULE.fizzbuzz
helper = MODULE.fizzbuzz_with_helper_func

PYTEST_TARGET = "tests/test_string.py::TestFizzbuzzFailurePath"
SOURCE = "algorithms/string/fizzbuzz.py"


def source_line(func, text):
    lines, start = inspect.getsourcelines(func)
    for offset, line in enumerate(lines):
        if text in line:
            return start + offset
    return None


def call(func, arg):
    """Return ("ok", result, None) or (exception name, message, line in func)."""
    try:
        return "ok", func(arg), None
    except Exception as exc:  # noqa: BLE001 - recording the outcome
        frames = traceback.extract_tb(exc.__traceback__)
        line = [f.lineno for f in frames if f.name == func.__name__][-1]
        return type(exc).__name__, str(exc), line


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
    results: list[dict] = []
    failures = 0

    guard = source_line(fizzbuzz, "if number < 1:")
    raise_value_error = source_line(fizzbuzz, 'raise ValueError("n cannot be less')
    none_check = source_line(fizzbuzz, "if number is None:")
    helper_body = source_line(helper, "return [_fb(value)")

    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    def check(label, func, arg, expected):
        nonlocal failures
        actual = call(func, arg)
        ok = actual == expected
        failures += not ok
        log(
            f"{'PASS' if ok else 'FAIL'} [{label}] {func.__name__}({arg!r}) "
            f"expected={expected!r} actual={actual!r}"
        )
        results.append(
            {
                "check": label,
                "call": f"{func.__name__}({arg!r})",
                "expected": list(expected),
                "actual": list(actual),
                "passed": ok,
            }
        )
        return actual

    log("R24-T048: fizzbuzz failure-path checks")
    expected_source = {
        "if number < 1:": guard,
        'raise ValueError("n cannot be less': raise_value_error,
        "if number is None:": none_check,
        "return [_fb(value)": helper_body,
    }
    for text, found in expected_source.items():
        if found is None:
            failures += 1
            log(f"FAIL [source] {text!r} not found in {SOURCE}")
    log(
        f"INFO [source] {SOURCE}: guard 'if number < 1' at L{guard}, "
        f"raise ValueError at L{raise_value_error}, 'if number is None' at "
        f"L{none_check}, fizzbuzz_with_helper_func body at L{helper_body}"
    )

    check("anchor", fizzbuzz, 5, ("ok", [1, 2, "Fizz", 4, "Buzz"], None))
    check("anchor", helper, 3, ("ok", [1, 2, "Fizz"], None))
    check("neighbor", fizzbuzz, 6, ("ok", [1, 2, "Fizz", 4, "Buzz", "Fizz"], None))
    check("neighbor", helper, 4, ("ok", [1, 2, "Fizz", 4], None))
    check("smallest valid", fizzbuzz, 1, ("ok", [1], None))

    before = fizzbuzz(3)
    check(
        "failure: smallest input reaching ValueError",
        fizzbuzz,
        0,
        ("ValueError", "n cannot be less than one", raise_value_error),
    )
    check(
        "failure: negative input",
        fizzbuzz,
        -2,
        ("ValueError", "n cannot be less than one", raise_value_error),
    )
    check(
        "failure: None raises at the guard comparison",
        fizzbuzz,
        None,
        (
            "TypeError",
            "'<' not supported between instances of 'NoneType' and 'int'",
            guard,
        ),
    )
    check(
        "after failure: valid call succeeds",
        fizzbuzz,
        5,
        ("ok", [1, 2, "Fizz", 4, "Buzz"], None),
    )
    ok = before == [1, 2, "Fizz"] and fizzbuzz(3) is not before
    failures += not ok
    log(
        f"{'PASS' if ok else 'FAIL'} [after failure: caller state] earlier "
        f"result expected=[1, 2, 'Fizz'] actual={before!r}, new call returns "
        f"a new list"
    )
    results.append(
        {"check": "caller state after failure", "actual": before, "passed": ok}
    )

    check("empty result: no guard", helper, 0, ("ok", [], None))
    check("empty result: no guard", helper, -3, ("ok", [], None))

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
                "source_lines": {
                    "guard_if_number_lt_1": guard,
                    "raise_value_error": raise_value_error,
                    "unreachable_if_number_is_none": none_check,
                    "helper_list_comprehension": helper_body,
                },
                "calls": [r["call"] for r in results if "call" in r],
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "checks": results,
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
