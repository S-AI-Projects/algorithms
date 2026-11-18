from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
file_path = root / "algorithms" / "sorting" / "cocktail_shaker_sort.py"

spec = importlib.util.spec_from_file_location("cocktail_shaker_sort", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cocktail_shaker_sort = module.cocktail_shaker_sort

def test_fixtures():
    # Fixture 1: [3, 1, 2] -> [1, 2, 3]
    assert cocktail_shaker_sort([3, 1, 2]) == [1, 2, 3]
    # Fixture 2: [2, 2, 1] -> [1, 2, 2] (multiplicity preservation)
    assert cocktail_shaker_sort([2, 2, 1]) == [1, 2, 2]
    # Fixture 3: already ordered [1, 2, 3] -> [1, 2, 3]
    assert cocktail_shaker_sort([1, 2, 3]) == [1, 2, 3]
    # Fixture 4: reversed [3, 2, 1] -> [1, 2, 3]
    assert cocktail_shaker_sort([3, 2, 1]) == [1, 2, 3]
    # Fixture 5: smallest supported collections
    assert cocktail_shaker_sort([]) == []
    assert cocktail_shaker_sort([1]) == [1]
    print("All standard fixtures passed.")

def test_mutation_contract():
    arr = [3, 1, 2]
    res = cocktail_shaker_sort(arr)
    assert res is arr, "Expected in-place sorting returning the same list instance"
    assert arr == [1, 2, 3]
    print("In-place mutation contract passed.")

def test_mutant_detection():
    # Plausible deliberate mutant: off-by-one in forward pass range(1, n - 1)
    def mutant_cocktail_sort(array: list[int]) -> list[int]:
        n = len(array)
        swapped = True
        while swapped:
            swapped = False
            for i in range(1, n - 1):  # BUG: misses last comparison array[n-2] > array[n-1]
                if array[i - 1] > array[i]:
                    array[i - 1], array[i] = array[i], array[i - 1]
                    swapped = True
            if not swapped:
                return array
            swapped = False
            for i in range(n - 1, 0, -1):
                if array[i - 1] > array[i]:
                    array[i - 1], array[i] = array[i], array[i - 1]
                    swapped = True
        return array

    # Test input where tail is out of order: [1, 3, 2]
    test_input = [1, 3, 2]
    expected = [1, 2, 3]

    # Original passes
    orig_output = cocktail_shaker_sort(list(test_input))
    assert orig_output == expected, f"Original failed: {orig_output}"

    # Mutant fails
    mutant_output = mutant_cocktail_sort(list(test_input))
    assert mutant_output != expected, f"Mutant unexpectedly passed: {mutant_output}"
    assert mutant_output == [1, 3, 2], f"Expected mutant output [1, 3, 2], got {mutant_output}"
    print("Mutation resistance verified: mutant was caught by [1, 3, 2].")

if __name__ == "__main__":
    test_fixtures()
    test_mutation_contract()
    test_mutant_detection()
    print("All checks in check.py passed successfully!")
