from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parents[2]
file_path = root / "algorithms" / "bit_manipulation" / "insert_bit.py"

spec = importlib.util.spec_from_file_location("insert_bit", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
insert_one_bit = module.insert_one_bit
insert_mult_bits = module.insert_mult_bits

def test_anchors():
    assert insert_one_bit(21, 1, 2) == 45
    assert insert_one_bit(21, 0, 2) == 41
    assert insert_mult_bits(5, 7, 3, 1) == 47
    print("Anchor fixture tests passed.")

def test_neighbors():
    assert insert_one_bit(21, 1, 0) == 43
    assert insert_one_bit(21, 0, 0) == 42
    assert insert_mult_bits(5, 7, 3, 0) == 47
    assert insert_mult_bits(5, 7, 3, 3) == 61
    print("Neighbor fixture tests passed.")

def test_repeatability_and_isolation():
    # First execution in fresh state
    res1 = insert_one_bit(21, 1, 2)
    assert res1 == 45, f"Expected 45, got {res1}"

    # Repeated identical execution
    res2 = insert_one_bit(21, 1, 2)
    assert res2 == 45, f"Expected 45, got {res2}"

    # Interleaved disparate calls
    insert_one_bit(1234, 1, 5)
    insert_mult_bits(99, 15, 4, 2)

    # Post-interleaving execution must remain completely unaltered
    res3 = insert_one_bit(21, 1, 2)
    assert res3 == 45, f"Expected 45, got {res3}"
    print("Repeatability and input isolation verified.")

def test_boundaries():
    assert insert_one_bit(0, 1, 0) == 1
    assert insert_one_bit(0, 0, 0) == 0
    print("Boundary tests passed.")

if __name__ == "__main__":
    test_anchors()
    test_neighbors()
    test_repeatability_and_isolation()
    test_boundaries()
    print("All checks in check.py passed successfully!")
