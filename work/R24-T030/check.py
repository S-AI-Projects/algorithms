"""Focused check for R24-T030: a regression test that catches a one-line bug.

Run from the repository root:

    python3 work/R24-T030/check.py

``is_prime(n, k)`` decides ``n < 5`` directly (only 2 and 3 are prime) and
runs k Miller-Rabin rounds from 5 up. Its only outside dependency is
``secrets.randbelow``, which picks the bases. Every mutation run below
replaces it with a fixed sequence, so the results are repeatable.

Mutants are built in memory from the source text. The working tree is never
edited, and the final source contains no mutant or test-only branch:

- P (primary, return condition): ``return n == 2 or n == 3`` ->
  ``return n <= 3``
- B (boundary comparison): ``if n < 5:`` -> ``if n < 6:``
- R (return condition): the final ``return True`` of ``_valid_witness`` ->
  ``return False``
- W (comparison): ``if x == 1 or x == n - 1:`` -> ``if x == 1:``

It exits non-zero if any of these fails:

1. The original passes every old and new test. The old test is
   TestRabinMiller.test_is_prime; the new ones are TestIsPrimeRegression.
2. Mutant P survives the old test but fails the named assertion
   TestIsPrimeRegression.test_one_is_not_prime with an AssertionError, a
   semantic failure rather than a crash. The inputs where P differs from the
   original are listed, reduced, and settled by trial division.
3. Every mutant fails at least one new test.
4. The invariant holds for the original on 0..199: every emitted prime has no
   divisor from 2 to its integer square root, 9 is rejected, and there are
   46 primes.
5. Docstrings aside, the code of rabin_miller.py is identical to the pinned
   commit bd1d152.
6. The focused tests (``TestIsPrimeRegression`` in ``tests/test_math.py``),
   run with pytest using the project's pytest settings from
   ``pyproject.toml``. A run that collects zero tests counts as a failure.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json, mutation.md and check_output.txt.
"""

from __future__ import annotations

import ast
import importlib.metadata
import importlib.util
import itertools
import json
import platform
import re
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
SOURCE = "algorithms/math/rabin_miller.py"
PINNED = "bd1d152f9ec7331c69be662831610b003b10fc7a"
sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test.
from algorithms.math.rabin_miller import is_prime  # noqa: E402

TEST_NODE = "tests/test_math.py::TestIsPrimeRegression"
PRIMARY = "P"
NAMED_ASSERTION = "TestIsPrimeRegression.test_one_is_not_prime"
MUTANTS = {
    "P": (
        "return condition",
        "        return n == 2 or n == 3\n",
        "        return n <= 3\n",
    ),
    "B": ("boundary comparison", "    if n < 5:\n", "    if n < 6:\n"),
    "R": (
        "return condition",
        "        return True\n\n    if n < 5:\n",
        "        return False\n\n    if n < 5:\n",
    ),
    "W": (
        "comparison",
        "        if x == 1 or x == n - 1:\n",
        "        if x == 1:\n",
    ),
}
OLD_TESTS = ["TestRabinMiller.test_is_prime"]
NEW_TESTS = [
    "TestIsPrimeRegression.test_one_is_not_prime",
    "TestIsPrimeRegression.test_fixture_domain_around_1_2_9_11",
    "TestIsPrimeRegression.test_primes_below_12_with_exclusive_upper_bound",
    "TestIsPrimeRegression.test_no_emitted_prime_has_a_divisor_up_to_its_square_root",
]


def fixed_randbelow():
    """Stand-in for secrets.randbelow: bases 2, 3, 5 and 7 in turn."""
    offsets = itertools.cycle([0, 1, 3, 5])
    return lambda bound: next(offsets) % bound


def prime_by_trial_division(n: int) -> bool:
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return n > 1


def build_mutant(source: str, key: str):
    _, old, new = MUTANTS[key]
    if source.count(old) != 1:
        raise RuntimeError(f"mutant {key}: anchor text not found exactly once")
    module = types.ModuleType(f"rabin_miller_mutant_{key}")
    exec(
        compile(source.replace(old, new), f"{SOURCE} (mutant {key})", "exec"),
        module.__dict__,
    )
    return module.is_prime


def load_test_module():
    spec = importlib.util.spec_from_file_location(
        "test_math_under_check", REPO_ROOT / "tests" / "test_math.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def error_line(traceback_text: str) -> str:
    """The exception line of a traceback, e.g. 'AssertionError: 46 != 45'."""
    lines = traceback_text.strip().splitlines()
    for line in lines:
        if re.match(r"^\w+(Error|Exception)\b", line):
            return line
    return lines[-1]


def run_tests(test_module, function) -> dict:
    """Run old and new tests with is_prime swapped for `function`."""
    outcomes = {}
    with mock.patch.object(test_module, "is_prime", function):
        for name in OLD_TESTS + NEW_TESTS:
            class_name, method = name.split(".")
            test = getattr(test_module, class_name)(method)
            result = unittest.TestResult()
            with mock.patch("secrets.randbelow", new=fixed_randbelow()):
                test.run(result)
            if result.errors:
                outcomes[name] = "error: " + error_line(result.errors[0][1])
            elif result.failures:
                outcomes[name] = "fail: " + error_line(result.failures[0][1])
            else:
                outcomes[name] = "pass"
    return outcomes


def call(function, n: int) -> object:
    with mock.patch("secrets.randbelow", new=fixed_randbelow()):
        try:
            return function(n, 4)
        except Exception as exc:
            return f"raised {type(exc).__name__}: {exc}"


def differing_inputs(function, limit: int) -> list[dict]:
    rows = []
    for n in range(limit):
        original, mutant = call(is_prime, n), call(function, n)
        if original != mutant:
            rows.append(
                {
                    "n": n,
                    "original": original,
                    "mutant": mutant,
                    "trial_division": prime_by_trial_division(n),
                }
            )
    return rows


def invariant_check() -> dict:
    emitted = [n for n in range(200) if call(is_prime, n) is True]
    with_divisor = [n for n in emitted if not prime_by_trial_division(n)]
    return {
        "emitted_count": len(emitted),
        "expected_count": 46,
        "emitted_with_a_small_divisor": with_divisor,
        "nine_rejected": call(is_prime, 9) is False,
        "primes_below_12": [n for n in range(12) if call(is_prime, n) is True],
        "passed": len(emitted) == 46
        and not with_divisor
        and call(is_prime, 9) is False,
    }


def strip_docstrings(source: str) -> str:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            body = node.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                node.body = body[1:] or [ast.Pass()]
    return ast.dump(tree)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


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


def mutation_markdown(table: dict, primary_diff: list[dict]) -> str:
    names = OLD_TESTS + NEW_TESTS
    short = {name: name.split(".")[1] for name in names}
    lines = [
        "# R24-T030 mutation analysis for is_prime",
        "",
        "Each cell is the outcome of one test with `secrets.randbelow` "
        "replaced by the fixed bases 2, 3, 5, 7. Old = TestRabinMiller; the "
        "others are the new TestIsPrimeRegression tests.",
        "",
        "| Version | Change | " + " | ".join(short[n] for n in names) + " |",
        "|---|---|" + "---|" * len(names),
    ]
    for version, row in table.items():
        change = "-" if version == "original" else MUTANTS[version][0]
        cells = " | ".join(row["outcomes"][n].split(":")[0] for n in names)
        lines.append(f"| {version} | {change} | {cells} |")
    lines += [
        "",
        "Primary mutant P (`return n == 2 or n == 3` -> `return n <= 3`): "
        "it survives the old test, which never calls is_prime below 5, and "
        "fails test_one_is_not_prime with an AssertionError. Inputs below 12 "
        "where P differs from the original: "
        + ", ".join(
            f"{r['n']} (original {r['original']}, mutant {r['mutant']}, "
            f"trial division says prime={r['trial_division']})"
            for r in primary_diff
        )
        + ". The reduced input is 1, the fixture value: it has a single "
        "divisor, so it is not prime.",
    ]
    return "\n".join(lines) + "\n"


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    source = (REPO_ROOT / SOURCE).read_text(encoding="utf-8")
    missing = [key for key, (_, old, _) in MUTANTS.items() if source.count(old) != 1]
    if missing:
        # The source no longer matches the code the mutants were written for,
        # for example because a mutant was left in it. Fail with a clear report.
        report = (
            "R24-T030 is_prime mutation check\n\n"
            f"[FAIL] {SOURCE} no longer contains the original line for mutant(s) "
            f"{missing}; the implementation has been changed\n\nOVERALL: FAIL\n"
        )
        (HERE / "check_output.txt").write_text(report, encoding="utf-8")
        print(report, end="")
        return 1
    test_module = load_test_module()

    table = {"original": {"outcomes": run_tests(test_module, is_prime)}}
    for key in MUTANTS:
        table[key] = {"outcomes": run_tests(test_module, build_mutant(source, key))}

    def killed_by(outcomes: dict, names: list[str]) -> list[str]:
        return [n for n in names if outcomes[n] != "pass"]

    for row in table.values():
        row["killed_by_old"] = killed_by(row["outcomes"], OLD_TESTS)
        row["killed_by_new"] = killed_by(row["outcomes"], NEW_TESTS)

    original_ok = (
        not table["original"]["killed_by_old"] + table["original"]["killed_by_new"]
    )
    primary = table[PRIMARY]["outcomes"]
    primary_ok = not table[PRIMARY]["killed_by_old"] and primary[
        NAMED_ASSERTION
    ].startswith("fail: AssertionError")
    all_killed = all(table[key]["killed_by_new"] for key in MUTANTS)
    primary_diff = differing_inputs(build_mutant(source, PRIMARY), 12)
    diff_ok = [r["n"] for r in primary_diff] == [0, 1] and all(
        r["original"] is False and r["trial_division"] is False for r in primary_diff
    )
    invariant = invariant_check()
    pinned_source = git("show", f"{PINNED}:{SOURCE}")
    code_unchanged = strip_docstrings(pinned_source) == strip_docstrings(source)
    pytest_result = run_pytest()

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    out = ["R24-T030 is_prime mutation check", ""]
    for version, row in table.items():
        label = (
            "original"
            if version == "original"
            else (f"mutant {version} ({MUTANTS[version][0]})")
        )
        out.append(
            f"{label}: killed by old tests {row['killed_by_old'] or 'none'}; "
            f"killed by new tests {len(row['killed_by_new'])}/{len(NEW_TESTS)}"
        )
        for name, outcome in row["outcomes"].items():
            out.append(f"    {name}: {outcome}")
    out.append("")
    out.append(f"[{mark(original_ok)}] original passes every old and new test")
    out.append(
        f"[{mark(primary_ok)}] mutant P survives the old test and fails "
        f"{NAMED_ASSERTION}: {primary[NAMED_ASSERTION]}"
    )
    out.append(f"[{mark(all_killed)}] every mutant fails at least one new test")
    out.append(
        f"[{mark(diff_ok)}] inputs below 12 where P differs: "
        f"{[(r['n'], r['original'], r['mutant']) for r in primary_diff]} "
        "(n, original, mutant); trial division says none of them is prime"
    )
    out.append(
        f"[{mark(invariant['passed'])}] invariant on 0..199: "
        f"{invariant['emitted_count']} emitted (expected 46), with a small "
        f"divisor: {invariant['emitted_with_a_small_divisor']}, 9 rejected: "
        f"{invariant['nine_rejected']}, primes below 12: "
        f"{invariant['primes_below_12']}"
    )
    out.append(
        f"[{mark(code_unchanged)}] code identical to {PINNED[:7]} apart from "
        "docstrings (no mutant or test-only branch)"
    )
    out.append("")
    out.append(f"Pytest command: {pytest_result['command']}")
    out.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    out.append(pytest_result["output"].rstrip())

    overall = (
        original_ok
        and primary_ok
        and all_killed
        and diff_ok
        and invariant["passed"]
        and code_unchanged
        and pytest_result["ok"]
    )
    out.append("")
    out.append("OVERALL: " + mark(overall))
    report = "\n".join(out) + "\n"

    write_json(
        "inputs.json",
        {
            "mutants": {
                k: {"kind": v[0], "from": v[1], "to": v[2]} for k, v in MUTANTS.items()
            },
            "primary_mutant": PRIMARY,
            "named_assertion": NAMED_ASSERTION,
            "fixed_bases": [2, 3, 5, 7],
            "rounds": 4,
            "fixture": {"1": False, "2": True, "9": False, "11": True},
            "primes_below_12": [2, 3, 5, 7, 11],
        },
    )
    write_json(
        "results.json",
        {
            "mutation_table": table,
            "primary_differing_inputs": primary_diff,
            "invariant": invariant,
            "code_unchanged_apart_from_docstrings": code_unchanged,
        },
    )
    write_json(
        "summary.json",
        {
            "task": "R24-T030",
            "target": "algorithms/math/rabin_miller.py:is_prime",
            "protected_condition": "n < 5: return n == 2 or n == 3",
            "primary_mutant": "return n == 2 or n == 3 -> return n <= 3",
            "named_assertion": NAMED_ASSERTION,
            "mutants_killed_by_old_tests": [
                k for k in MUTANTS if table[k]["killed_by_old"]
            ],
            "mutants_killed_by_new_tests": [
                k for k in MUTANTS if table[k]["killed_by_new"]
            ],
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": mark(overall),
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "mutation.md").write_text(
        mutation_markdown(table, primary_diff), encoding="utf-8"
    )
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
