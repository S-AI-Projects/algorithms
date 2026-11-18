from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parents[2]
file_path = root / "algorithms" / "array" / "delete_nth.py"

spec = importlib.util.spec_from_file_location("delete_nth", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
delete_nth_naive = module.delete_nth_naive

def oracle(array, n):
    """Independent oracle: uses simple scan over output collection without list.count()."""
    res = []
    for item in array:
        count = sum(1 for x in res if x == item)
        if count < n:
            res.append(item)
    return res

def test_anchor():
    inp = [1, 2, 3, 1, 2, 1, 2, 3]
    expected = [1, 2, 3, 1, 2, 3]
    actual = delete_nth_naive(inp, 2)
    assert actual == expected, f"Expected {expected}, got {actual}"
    print("Anchor fixture test passed.")

def test_neighbor():
    inp = [1, 2, 3, 1, 2, 1, 2, 3]
    expected = [1, 2, 3]
    actual = delete_nth_naive(inp, 1)
    assert actual == expected, f"Expected {expected}, got {actual}"
    print("Neighbor fixture test passed.")

def test_twenty_cases():
    cases = [
        ([], 0),
        ([], 1),
        ([1], 0),
        ([1], 1),
        ([1, 1], 1),
        ([1, 1], 2),
        ([1, 2, 3], 1),
        ([1, 2, 3], 2),
        ([1, 2, 3, 1, 2, 1, 2, 3], 2),
        ([1, 2, 3, 1, 2, 1, 2, 3], 1),
        ([1, 2, 3, 1, 2, 1, 2, 3], 3),
        ([5, 5, 5, 5, 5], 1),
        ([5, 5, 5, 5, 5], 3),
        ([5, 5, 5, 5, 5], 5),
        ([1, 2, 1, 2, 1, 2], 0),
        ([3, 1, 4, 1, 5, 9, 2, 6, 5], 1),
        ([3, 1, 4, 1, 5, 9, 2, 6, 5], 2),
        ([0, 0, 0], 1),
        ([-1, -2, -1, -3, -2], 1),
        ([-5, 10, -5, 20, 10], 2),
        ([42], 5),
        ([7, 7, 8, 8, 7, 8], 2),
    ]
    for i, (arr, n) in enumerate(cases, 1):
        expected = oracle(arr, n)
        actual = delete_nth_naive(arr, n)
        assert actual == expected, f"Case {i} failed for ({arr}, {n}): expected {expected}, got {actual}"
    print(f"All {len(cases)} independent oracle cross-checks passed.")

def test_immutability():
    arr = [1, 2, 3, 1, 2, 1, 2, 3]
    copy_arr = list(arr)
    delete_nth_naive(arr, 2)
    assert arr == copy_arr, "Input array was mutated!"
    print("Input immutability test passed.")

if __name__ == "__main__":
    test_anchor()
    test_neighbor()
    test_twenty_cases()
    test_immutability()
    print("All checks in check.py passed successfully!")
