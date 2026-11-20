#!/usr/bin/env python3
"""Focused check runner for R24-T045: deterministic execution of int_to_base.

Dependency inventory for int_to_base (algorithms/math/base_conversion.py):
    - string.digits + string.ascii_uppercase: constant ASCII digit alphabet.
    - No file, network, time, randomness, environment, locale, UI or
      mutable global state. It is a pure function, so nothing needs a seam;
      the checks verify purity instead of mocking a real dependency.

Checks:
1. Fixture (source anchors + neighbor 256 -> "100") in this process.
2. The same fixture in two fresh isolated interpreters (python -I).
3. The fixture again after other valid inputs, to show earlier calls cannot
   change later results.
4. The caller's argument values are unchanged after the call.
5. The fixture with open/socket/time/random/os.getenv patched to fail, to
   show none of them is used.
6. Independent decoding: int(int_to_base(n, b), b) == n for n in -40..40
   and every base 2..36.
7. The focused pytest class with the project's pytest configuration:
   tests/test_math.py::TestIntToBaseDeterminism

Writes evidence to work/R24-T045/ and exits non-zero if any check fails.

Usage:
    python3 work/R24-T045/check.py
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R24-T045"
sys.path.insert(0, str(ROOT))

from algorithms.math.base_conversion import int_to_base  # noqa: E402

PYTEST_TARGET = "tests/test_math.py::TestIntToBaseDeterminism"

# (num, base, expected, how the expected value was derived)
FIXTURE = [
    (5, 2, "101", "anchor: 5 = 4 + 1"),
    (255, 16, "FF", "anchor: 255 = 15 * 16 + 15"),
    (0, 2, "0", "anchor: zero"),
    (256, 16, "100", "neighbor of 255: 256 = 1 * 16 ** 2"),
]
EXPECTED = [expected for _, _, expected, _ in FIXTURE]

OTHER_INPUTS = [
    (-1000, 7, "-2626", "1000 = 2*343 + 6*49 + 2*7 + 6"),
    (2**64, 16, "10000000000000000", "2**64 = 16**16"),
    (35, 36, "Z", "largest digit of base 36"),
]

FRESH_SCRIPT = (
    "import json, sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "from algorithms.math.base_conversion import int_to_base\n"
    "cases = json.loads(sys.argv[2])\n"
    "print(json.dumps([int_to_base(n, b) for n, b in cases]))\n"
)

DEPENDENCY_INVENTORY = {
    "string.digits + string.ascii_uppercase": "constant ASCII digit alphabet",
    "file / network I/O": "none",
    "time / clock": "none",
    "randomness": "none",
    "environment / locale": "none",
    "mutable global state": "none",
    "UI / user account": "none",
}


def run_fixture():
    return [int_to_base(num, base) for num, base, _, _ in FIXTURE]


def run_fresh_process():
    cases = json.dumps([[n, b] for n, b, _, _ in FIXTURE])
    proc = subprocess.run(
        [sys.executable, "-I", "-c", FRESH_SCRIPT, str(ROOT), cases],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return f"error: {proc.stderr.strip()[-300:]}"
    return json.loads(proc.stdout)


def run_with_dependencies_blocked():
    forbidden = AssertionError("int_to_base used an external dependency")
    patches = [
        "builtins.open",
        "socket.socket",
        "time.time",
        "time.monotonic",
        "random.random",
        "random.getrandbits",
        "os.getenv",
    ]
    managers = [mock.patch(target, side_effect=forbidden) for target in patches]
    for manager in managers:
        manager.start()
    try:
        return run_fixture(), patches
    except AssertionError as exc:
        return f"error: {exc}", patches
    finally:
        for manager in managers:
            manager.stop()


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

    def check(label, expected, actual):
        nonlocal failures
        ok = actual == expected
        failures += not ok
        msg = f"{'PASS' if ok else 'FAIL'} [{label}] expected={expected!r} "
        msg += f"actual={actual!r}"
        print(msg)
        lines.append(msg)
        results.append(
            {"check": label, "expected": expected, "actual": actual, "passed": ok}
        )

    def log(msg: str) -> None:
        print(msg)
        lines.append(msg)

    log("R24-T045: int_to_base deterministic execution checks")
    for name, use in DEPENDENCY_INVENTORY.items():
        log(f"INFO [dependency] {name}: {use}")

    for num, base, expected, _ in FIXTURE:
        check(f"fixture int_to_base({num}, {base})", expected, int_to_base(num, base))

    check("fresh process run 1 (python -I)", EXPECTED, run_fresh_process())
    check("fresh process run 2 (python -I)", EXPECTED, run_fresh_process())

    before = run_fixture()
    for num, base, expected, _ in OTHER_INPUTS:
        check(
            f"other input int_to_base({num}, {base})", expected, int_to_base(num, base)
        )
    check("fixture before other inputs", EXPECTED, before)
    check("fixture after other inputs", EXPECTED, run_fixture())

    num, base = -255, 16
    output = int_to_base(num, base)
    check("caller value: int_to_base(-255, 16)", "-FF", output)
    check("caller value: num and base unchanged", (-255, 16), (num, base))

    blocked, patched = run_with_dependencies_blocked()
    check(f"fixture with {len(patched)} dependencies blocked", EXPECTED, blocked)

    decode_failures = [
        (n, b)
        for b in range(2, 37)
        for n in range(-40, 41)
        if int(int_to_base(n, b), b) != n
    ]
    check("int(int_to_base(n, b), b) == n for 2835 inputs", [], decode_failures)

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
                "fixture": [
                    {"num": n, "base": b, "expected": e, "derivation": d}
                    for n, b, e, d in FIXTURE
                ],
                "other_inputs": [
                    {"num": n, "base": b, "expected": e, "derivation": d}
                    for n, b, e, d in OTHER_INPUTS
                ],
                "blocked_dependencies": patched,
                "decode_range": {"num": "-40..40", "base": "2..36"},
            },
            indent=2,
        )
        + "\n"
    )
    (WORK / "results.json").write_text(
        json.dumps(
            {
                "dependency_inventory": DEPENDENCY_INVENTORY,
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
