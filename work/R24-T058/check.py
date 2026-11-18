from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
file_path = root / "algorithms" / "matrix" / "matrix_exponentiation.py"

spec = importlib.util.spec_from_file_location("matrix_exponentiation", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
multiply = module.multiply

def test_one_by_one():
    res = multiply([[3]], [[4]])
    assert res == [[12]], f"Expected [[12]], got {res}"
    print("1x1 matrix test passed.")

def test_zero_containing():
    a = [[0, 2], [3, 0]]
    b = [[1, 0], [0, 4]]
    res = multiply(a, b)
    assert res == [[0, 8], [3, 0]], f"Expected [[0, 8], [3, 0]], got {res}"
    print("Zero-containing matrix test passed.")

def test_empty_absent_result():
    res = multiply([], [])
    assert res == [], f"Expected [], got {res}"
    print("Empty absent-result boundary test passed.")

def test_rectangular_failure_and_recovery():
    a = [[1], [2]]
    b = [[3], [4]]
    copy_a = [list(r) for r in a]
    copy_b = [list(r) for r in b]

    # Exercise failure path
    try:
        multiply(a, b)
        assert False, "Expected IndexError on incompatible rectangular input"
    except IndexError:
        print("Failure branch (IndexError) reached as expected.")

    # Assert caller-owned state remained intact
    assert a == copy_a, "Caller state `a` was mutated!"
    assert b == copy_b, "Caller state `b` was mutated!"

    # Assert successful execution afterwards
    valid_res = multiply([[1, 0], [0, 1]], [[2, 3], [4, 5]])
    assert valid_res == [[2, 3], [4, 5]], f"Expected [[2, 3], [4, 5]], got {valid_res}"
    print("Recovery: subsequent valid call succeeded.")

if __name__ == "__main__":
    test_one_by_one()
    test_zero_containing()
    test_empty_absent_result()
    test_rectangular_failure_and_recovery()
    print("All checks in check.py passed successfully!")
