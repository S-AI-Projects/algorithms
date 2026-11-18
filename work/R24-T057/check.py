from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
file_path = root / "algorithms" / "array" / "trimmean.py"

spec = importlib.util.spec_from_file_location("trimmean", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
trimmean = module.trimmean

def test_anchor():
    res = trimmean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 20)
    assert res == 5.5, f"Expected 5.5, got {res}"
    print("Anchor test passed.")

def test_neighbor_forty():
    res = trimmean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 40)
    assert res == 5.5, f"Expected 5.5, got {res}"
    print("Neighbor 40% test passed.")

def test_documented_walkthrough():
    arr = [10.0, 2.0, 4.0, 8.0, 6.0]
    res = trimmean(arr, 40)
    assert res == 6.0, f"Expected 6.0, got {res}"
    print("Documented walkthrough test passed.")

def test_boundary_zero():
    res = trimmean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0)
    assert res == 5.5, f"Expected 5.5, got {res}"
    print("Boundary zero percent test passed.")

def test_in_place_sort():
    arr = [5.0, 1.0, 3.0]
    trimmean(arr, 0)
    assert arr == [1.0, 3.0, 5.0], "Expected array to be sorted in place"
    print("In-place sort test passed.")

if __name__ == "__main__":
    test_anchor()
    test_neighbor_forty()
    test_documented_walkthrough()
    test_boundary_zero()
    test_in_place_sort()
    print("All checks in check.py passed successfully!")
