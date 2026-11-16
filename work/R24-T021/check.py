"""Focused check for R24-T021: contract of delete_reoccurring_characters.

Run from the repository root:

    python3 work/R24-T021/check.py

It does two things and exits non-zero if either fails:

1. Runs the focused regression tests (``TestDeleteReoccurring`` in
   ``tests/test_string.py``) with pytest, using the project's pytest settings
   from ``pyproject.toml``. A run that collects zero tests counts as a failure.
2. Calls ``delete_reoccurring_characters`` directly on a fixed table of inputs
   whose expected outputs were worked out by hand, and checks that each input
   string is unchanged after the call.

The function does no I/O, so there is nothing external to mock.

Evidence is written next to this file: inputs.json, results.json,
summary.json, tool_versions.json and check_output.txt.
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import only the module under test.
from algorithms.string.delete_reoccurring import (  # noqa: E402
    delete_reoccurring_characters,
)

TEST_NODE = "tests/test_string.py::TestDeleteReoccurring"

# Expected values derived by hand from the contract, before running the code.
CASES = [
    {"name": "fixture", "input": "aaabcccc", "expected": "abc"},
    {"name": "neighbour_non_adjacent_repeat", "input": "aaabcccca", "expected": "abc"},
    {"name": "neighbour_new_char_appended", "input": "aaabccccd", "expected": "abcd"},
    {"name": "smallest_empty", "input": "", "expected": ""},
    {"name": "single_char", "input": "z", "expected": "z"},
    {"name": "boundary_all_identical", "input": "aaaa", "expected": "a"},
    {"name": "boundary_all_distinct", "input": "abcd", "expected": "abcd"},
    {"name": "case_sensitive", "input": "aA", "expected": "aA"},
]


def run_direct_cases() -> list[dict]:
    results = []
    for case in CASES:
        argument = case["input"]
        actual = delete_reoccurring_characters(argument)
        value_ok = actual == case["expected"]
        unchanged = argument == case["input"]
        results.append(
            {
                "name": case["name"],
                "input": case["input"],
                "expected": case["expected"],
                "actual": actual,
                "value_ok": value_ok,
                "input_unchanged": unchanged,
                "passed": value_ok and unchanged,
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


def write_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    direct = run_direct_cases()
    pytest_result = run_pytest()

    lines = ["R24-T021 delete_reoccurring_characters contract check", ""]
    lines.append("Direct cases (expected vs actual):")
    for r in direct:
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(
            f"  [{status}] {r['name']}: input={r['input']!r} "
            f"expected={r['expected']!r} actual={r['actual']!r} "
            f"input_unchanged={r['input_unchanged']}"
        )
    lines.append("")
    lines.append(f"Pytest command: {pytest_result['command']}")
    lines.append(
        f"Pytest result: {pytest_result['passed']} passed, "
        f"{pytest_result['failed']} failed, exit {pytest_result['returncode']}"
    )
    lines.append(pytest_result["output"].rstrip())

    direct_ok = all(r["passed"] for r in direct)
    overall = direct_ok and pytest_result["ok"]
    lines.append("")
    lines.append("OVERALL: " + ("PASS" if overall else "FAIL"))
    report = "\n".join(lines) + "\n"

    write_json("inputs.json", CASES)
    write_json("results.json", direct)
    write_json(
        "summary.json",
        {
            "task": "R24-T021",
            "target": "algorithms/string/delete_reoccurring.py:"
            "delete_reoccurring_characters",
            "direct_cases": len(direct),
            "direct_cases_passed": sum(r["passed"] for r in direct),
            "pytest_command": pytest_result["command"],
            "pytest_passed": pytest_result["passed"],
            "pytest_failed": pytest_result["failed"],
            "overall": "PASS" if overall else "FAIL",
        },
    )
    write_json("tool_versions.json", tool_versions())
    (HERE / "check_output.txt").write_text(report, encoding="utf-8")

    print(report, end="")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
