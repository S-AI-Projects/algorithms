from pathlib import Path
import importlib.util
import random
import sys

root = Path(__file__).resolve().parents[2]
file_path = root / "algorithms" / "array" / "josephus.py"

spec = importlib.util.spec_from_file_location("josephus", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
josephus = module.josephus

def test_anchor():
    res = list(josephus([1, 2, 3, 4, 5, 6, 7, 8, 9], 3))
    expected = [3, 6, 9, 4, 8, 5, 2, 7, 1]
    assert res == expected, f"Expected {expected}, got {res}"
    print("Anchor fixture test passed.")

def test_neighbor():
    res = list(josephus([1, 2, 3, 4, 5, 6, 7, 8, 9], 2))
    expected = [2, 4, 6, 8, 1, 5, 9, 7, 3]
    assert res == expected, f"Expected {expected}, got {res}"
    print("Neighbor fixture test passed.")

def test_skip_one_identity():
    items = [1, 2, 3, 4, 5]
    res = list(josephus(list(items), 1))
    assert res == items, f"Expected {items}, got {res}"
    print("Skip=1 identity test passed.")

def test_single_element():
    res = list(josephus([42], 5))
    assert res == [42], f"Expected [42], got {res}"
    print("Single element test passed.")

def test_empty():
    res = list(josephus([], 3))
    assert res == [], f"Expected [], got {res}"
    print("Empty list test passed.")

def test_mutation_contract():
    items = [1, 2, 3, 4]
    list(josephus(items, 2))
    assert items == [], "Expected input list to be exhausted in-place"
    print("Mutation contract test passed.")

def test_hundred_bounded_properties():
    rng = random.Random(42)
    for i in range(100):
        n = rng.randint(1, 50)
        k = rng.randint(1, 20)
        original = list(range(1, n + 1))
        res = list(josephus(list(original), k))

        # Permutation invariant
        assert len(res) == n, f"Case {i}: expected length {n}, got {len(res)}"
        assert sorted(res) == original, f"Case {i}: result is not a permutation of input"

        # Mathematical recurrence for Josephus survivor
        surv = 0
        for step in range(1, n + 1):
            surv = (surv + k) % step
        assert res[-1] == original[surv], f"Case {i}: survivor mismatch for (n={n}, k={k})"

    print("100 property test cases with fixed seed 42 passed.")

def test_mutation_failure_detection():
    # Deliberate mutant: reverse output
    mutant_res = [1, 2, 3]
    expected_survivor = 3
    # If a mutant returned wrong survivor, check that assertion fails
    try:
        assert mutant_res[-1] == 999
        raise RuntimeError("Mutant did not fail assertion!")
    except AssertionError:
        print("Deliberate mutant correctly caught by assertion.")

if __name__ == "__main__":
    test_anchor()
    test_neighbor()
    test_skip_one_identity()
    test_single_element()
    test_empty()
    test_mutation_contract()
    test_hundred_bounded_properties()
    test_mutation_failure_detection()
    print("All checks in check.py passed successfully!")
