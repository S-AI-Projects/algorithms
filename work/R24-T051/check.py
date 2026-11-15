from pathlib import Path
import importlib.util

# Locate the original Python file
root = Path(__file__).resolve().parents[2]

file_path = root / "algorithms" / "linked_list" / "remove_duplicates.py"

# Load only the required module
spec = importlib.util.spec_from_file_location(
    "remove_duplicates", file_path
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

Node = module.Node


def test_three_nodes():
    # Create three different nodes
    a = Node(10)
    b = Node(20)
    c = Node(30)

    # Connect them: A -> B -> C
    a.next = b
    b.next = c

    # Check the values
    assert a.val == 10
    assert b.val == 20
    assert c.val == 30

    # Check the actual node connections
    assert a.next is b
    assert b.next is c
    assert c.next is None

    print("Three-node test passed!")


def test_single_node():
    a = Node(10)

    assert a.val == 10
    assert a.next is None

    print("Single-node test passed!")

def test_remove_duplicates():
    a = Node(10)
    b = Node(20)
    c = Node(10)

    a.next = b
    b.next = c

    result = module.remove_dups(a)

    assert result is None
    assert a.val == 10
    assert b.val == 20
    assert a.next is b
    assert b.next is None

    print("Duplicate removal test passed!")


def test_no_duplicates():
    a = Node(10)
    b = Node(20)
    c = Node(30)

    a.next = b
    b.next = c

    result = module.remove_dups(a)

    assert result is None
    assert [a.val, b.val, c.val] == [10, 20, 30]
    assert a.next is b
    assert b.next is c
    assert c.next is None

    print("No-duplicates test passed!")

def test_without_set():
    a = Node(10)
    b = Node(20)
    c = Node(10)

    a.next = b
    b.next = c

    result = module.remove_dups_without_set(a)

    assert result is None
    assert a.val == 10
    assert b.val == 20

    assert a.next is b
    assert b.next is None

    print("Without-set test passed!")


if __name__ == "__main__":
    test_without_set()
    test_three_nodes()
    test_single_node()
    test_remove_duplicates()
    test_no_duplicates()
    
    print("All 5 tests passed!")