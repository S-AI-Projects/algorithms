from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parents[2]
file_path = root / "algorithms" / "dynamic_programming" / "planting_trees.py"

spec = importlib.util.spec_from_file_location("planting_trees", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
planting_trees = module.planting_trees

def test_anchor():
    trees = [0, 1, 10, 10]
    expected = 2.414213562373095
    actual = planting_trees(trees, 10, 1)
    assert abs(actual - expected) < 1e-9, f"Expected {expected}, got {actual}"
    print("Anchor fixture test passed.")

def test_neighbor_aligned():
    trees = [0, 0, 10, 10]
    expected = 2.0
    actual = planting_trees(trees, 10, 1)
    assert actual == expected, f"Expected {expected}, got {actual}"
    print("Neighbor aligned test passed.")

def test_width_boundary():
    trees = [0, 0, 10, 10]
    expected = 0.0
    actual = planting_trees(trees, 10, 0)
    assert actual == expected, f"Expected {expected}, got {actual}"
    print("Width zero boundary test passed.")

def test_length_and_width_boundary():
    trees = [0, 0, 0, 0]
    expected = 0.0
    actual = planting_trees(trees, 0, 0)
    assert actual == expected, f"Expected {expected}, got {actual}"
    print("Length and width zero boundary test passed.")

def test_smallest_supported():
    trees = [1, 2, 3, 4]
    expected = 4.0
    actual = planting_trees(trees, 3, 0)
    assert actual == expected, f"Expected {expected}, got {actual}"
    print("Smallest supported collection test passed.")

def test_immutability():
    trees = [0, 1, 10, 10]
    copy_trees = list(trees)
    planting_trees(trees, 10, 1)
    assert trees == copy_trees, "Input list was mutated!"
    print("Input immutability test passed.")

def test_unsupported():
    try:
        planting_trees([1, 2], 10, 1)
        assert False, "Expected ZeroDivisionError was not raised"
    except ZeroDivisionError:
        print("Unsupported boundary correctly raised ZeroDivisionError.")

if __name__ == "__main__":
    test_anchor()
    test_neighbor_aligned()
    test_width_boundary()
    test_length_and_width_boundary()
    test_smallest_supported()
    test_immutability()
    test_unsupported()
    print("All 7 checks in check.py passed successfully!")
