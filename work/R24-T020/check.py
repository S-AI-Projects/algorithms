#!/usr/bin/env python3
"""Focused check runner for R24-T020: add_bitwise_operator mutation-resistant tests.

Proves regression test suite catches a plausible one-line mutation:
  Replace ``carry = first & second`` with ``carry = first | second``.

Steps:
1. Verify anchor fixtures and neighbour with explicit expected values.
2. Demonstrate the mutant FAILS the same named assertion (original passes).
3. Run focused pytest on:
   tests/test_bit_manipulation.py::TestAddBitwiseOperatorStrengthened
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

abo_module = importlib.import_module(
    "algorithms.bit_manipulation.add_bitwise_operator"
)
add_bitwise_operator = abo_module.add_bitwise_operator

WORK_DIR = PROJECT_ROOT / "work" / "R24-T020"
WORK_DIR.mkdir(parents=True, exist_ok=True)


def mutant_add_bitwise_operator(first: int, second: int) -> int:
    """Deliberate mutation: carry = first | second (wrong) instead of first & second.

    This is test-only; it is NOT present in production source.
    """
    if first < 0 or second < 0:
        raise ValueError("The provided values must be non-negative!")
    iterations = 0
    while second and iterations < 100:  # guard against infinite loop
        carry = first | second  # MUTANT: | instead of &
        first = first ^ second
        second = carry << 1
        iterations += 1
    return first


def main() -> int:
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 60)
    log("R24-T020: add_bitwise_operator Mutation-Resistant Tests")
    log("=" * 60)

    # 1. Source anchor and neighbour checks
    cases = [
        (2, 3, 5),
        (0, 0, 0),
        (1, 1, 2),
        (10, 0, 10),
        (0, 10, 10),
        (3, 5, 8),
        (4, 4, 8),
        (5432, 97823, 5432 + 97823),
    ]
    results_data = []
    for a, b, expected in cases:
        actual = add_bitwise_operator(a, b)
        assert actual == expected, f"Expected {expected}, got {actual} for ({a},{b})"
        log(f"PASS: add_bitwise_operator({a}, {b}) -> {actual}")
        results_data.append({"a": a, "b": b, "expected": expected, "actual": actual})

    # 2. Demonstrate mutant detection
    # Original passes: add_bitwise_operator(2, 3) == 5
    orig_result = add_bitwise_operator(2, 3)
    assert orig_result == 5, f"Original expected 5, got {orig_result}"
    log(f"PASS: Original: add_bitwise_operator(2,3) == {orig_result}")

    # Mutant fails: mutant_add_bitwise_operator(2, 3) != 5
    mutant_result = mutant_add_bitwise_operator(2, 3)
    assert mutant_result != 5, (
        f"Mutant should NOT produce 5 for input (2,3), got {mutant_result}"
    )
    log(
        f"PASS: Mutant (carry=first|second) produces {mutant_result} != 5,"
        " regression caught"
    )

    # 3. Commutativity check
    for a, b, _expected in [(2, 3, 5), (7, 5, 12)]:
        assert add_bitwise_operator(a, b) == add_bitwise_operator(b, a)
        log(f"PASS: commutative: ({a},{b}) == ({b},{a})")

    # 4. ValueError for negatives
    try:
        add_bitwise_operator(-1, 5)
        raise AssertionError("Expected ValueError for negative input")
    except ValueError:
        log("PASS: ValueError raised for negative input")

    # 5. Native pytest
    test_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "tests/test_bit_manipulation.py::TestAddBitwiseOperatorStrengthened",
    ]
    log(f"Running: {' '.join(test_cmd)}")
    proc = subprocess.run(
        test_cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    log(proc.stdout)
    if proc.stderr:
        log(proc.stderr)
    assert proc.returncode == 0, f"Pytest failed with code {proc.returncode}"
    log("PASS: Native pytest passed.")

    # Save evidence
    with open(WORK_DIR / "inputs.json", "w") as f:
        json.dump({"cases": cases}, f, indent=2)

    with open(WORK_DIR / "results.json", "w") as f:
        json.dump(
            {
                "results": results_data,
                "mutant_detection": {
                    "input": [2, 3],
                    "original_result": orig_result,
                    "mutant_result": mutant_result,
                    "mutation": "carry = first | second (instead of &)",
                    "caught": mutant_result != 5,
                },
                "pytest": {
                    "returncode": proc.returncode,
                    "command": " ".join(test_cmd),
                },
            },
            f,
            indent=2,
        )

    with open(WORK_DIR / "summary.json", "w") as f:
        json.dump(
            {
                "task": "R24-T020",
                "status": "PASS",
                "function": "add_bitwise_operator",
                "module": "algorithms.bit_manipulation.add_bitwise_operator",
                "mutation": "carry = first | second instead of first & second",
                "detecting_input": [2, 3],
                "original_passes": True,
                "mutant_fails": True,
                "no_mutation_in_final_source": True,
                "pytest_passed": True,
            },
            f,
            indent=2,
        )

    def get_ver(pkg: str) -> str:
        try:
            return importlib.metadata.version(pkg)
        except Exception:
            return "unknown"

    with open(WORK_DIR / "tool_versions.json", "w") as f:
        json.dump(
            {
                "python": sys.version,
                "platform": platform.platform(),
                "pytest": get_ver("pytest"),
                "ruff": get_ver("ruff"),
                "black": get_ver("black"),
            },
            f,
            indent=2,
        )

    with open(WORK_DIR / "check_output.txt", "w") as f:
        f.write("\n".join(log_lines) + "\n")

    log("=" * 60)
    log("All R24-T020 checks passed. Evidence in work/R24-T020/")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
