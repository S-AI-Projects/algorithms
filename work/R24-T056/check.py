from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
file_path = root / "algorithms" / "tree" / "is_subtree.py"

spec = importlib.util.spec_from_file_location("is_subtree", file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
is_subtree = module.is_subtree
TreeNode = module.TreeNode

def test_anchor():
    node = TreeNode(1)
    assert is_subtree(node, node) is True
    print("Anchor test passed.")

def test_neighbor_left():
    big = TreeNode(1)
    big.left = TreeNode(2)
    big.right = TreeNode(3)
    small = TreeNode(2)
    assert is_subtree(big, small) is True
    print("Neighbor left test passed.")

def test_neighbor_right():
    big = TreeNode(1)
    big.left = TreeNode(2)
    big.right = TreeNode(3)
    small = TreeNode(3)
    assert is_subtree(big, small) is True
    print("Neighbor right test passed.")

def test_mismatch_value():
    big = TreeNode(1)
    big.left = TreeNode(2)
    small = TreeNode(4)
    assert is_subtree(big, small) is False
    print("Mismatch value test passed.")

def test_mismatch_structure():
    big = TreeNode(1)
    big.left = TreeNode(2)
    small = TreeNode(2)
    small.left = TreeNode(3)
    assert is_subtree(big, small) is False
    print("Mismatch structure test passed.")

def test_deep_tree():
    big = TreeNode(10)
    big.left = TreeNode(5)
    big.left.left = TreeNode(2)
    big.left.right = TreeNode(7)
    big.right = TreeNode(15)

    small = TreeNode(5)
    small.left = TreeNode(2)
    small.right = TreeNode(7)
    assert is_subtree(big, small) is True
    print("Deep subtree test passed.")

if __name__ == "__main__":
    test_anchor()
    test_neighbor_left()
    test_neighbor_right()
    test_mismatch_value()
    test_mismatch_structure()
    test_deep_tree()
    print("All checks in check.py passed successfully!")
