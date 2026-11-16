"""
Separate Chaining Hash Table

Hash table implementation using separate chaining (linked lists) for
collision resolution.

Reference: https://en.wikipedia.org/wiki/Hash_table#Separate_chaining

Complexity:
    Time:  O(1) average for put/get/del, O(n) worst case
    Space: O(n)
"""

from __future__ import annotations


class _Node:
    """Internal linked list node for bucket chaining.

    Worked Example:
        Step 1 (Initial node creation):
        >>> n1 = _Node('hello', 'world')
        >>> n1.key
        'hello'
        >>> n1.value
        'world'
        >>> n1.next is None
        True

        Step 2 (Chaining intermediate collision node):
        >>> n2 = _Node('foo', 'bar', next_node=n1)
        >>> n2.key, n2.value
        ('foo', 'bar')
        >>> n2.next is n1
        True
        >>> n2.next.key, n2.next.value
        ('hello', 'world')

        Step 3 (In-place value update on existing node):
        >>> n1.value = 'updated_world'
        >>> n2.next.value
        'updated_world'

    Decisive State Transitions:
        - Insertion into empty bucket: `_table[hash]` transitions from `None`
          to a new `_Node(key, value)`.
        - Collision chaining: existing tail `node_.next` transitions from `None`
          to a newly linked `_Node(key, value)`.
        - Existing key update: `node_.value` updates in-place while retaining
          its `next` pointer and without altering the table length.

    Args:
        key: The key stored in this node.
        value: The value stored in this node.
        next_node: Reference to the next node in the chain.
    """

    def __init__(
        self,
        key: object = None,
        value: object = None,
        next_node: _Node | None = None,
    ) -> None:
        self.key = key
        self.value = value
        self.next = next_node


class SeparateChainingHashTable:
    """Hash table using separate chaining for collision resolution.

    Examples:
        >>> table = SeparateChainingHashTable()
        >>> table.put('hello', 'world')
        >>> len(table)
        1
        >>> # Neighboring supported input:
        >>> table.put('foo', 'bar')
        >>> len(table)
        2
        >>> table.get('hello')
        'world'
        >>> table.get('foo')
        'bar'
        >>> del table['hello']
        >>> table.get('hello') is None
        True
        >>> len(table)
        1
    """

    _empty = None

    def __init__(self, size: int = 11) -> None:
        """Initialize the hash table.

        Args:
            size: Number of buckets.
        """
        self.size = size
        self._len = 0
        self._table: list[_Node | None] = [self._empty] * size

    def put(self, key: object, value: object) -> None:
        """Insert or update a key-value pair.

        Args:
            key: The key to insert.
            value: The value associated with the key.
        """
        hash_ = self.hash(key)
        node_ = self._table[hash_]
        if node_ is self._empty:
            self._table[hash_] = _Node(key, value)
        else:
            while node_.next is not None:
                if node_.key == key:
                    node_.value = value
                    return
                node_ = node_.next
            if node_.key == key:
                node_.value = value
                return
            node_.next = _Node(key, value)
        self._len += 1

    def get(self, key: object) -> object | None:
        """Retrieve the value for a given key.

        Args:
            key: The key to look up.

        Returns:
            The associated value, or None if the key is not found.
        """
        hash_ = self.hash(key)
        node_ = self._table[hash_]
        while node_ is not self._empty:
            if node_.key == key:
                return node_.value
            node_ = node_.next
        return None

    def del_(self, key: object) -> None:
        """Delete a key-value pair.

        Args:
            key: The key to delete.
        """
        hash_ = self.hash(key)
        node_ = self._table[hash_]
        previous_node = None
        while node_ is not None:
            if node_.key == key:
                if previous_node is None:
                    self._table[hash_] = node_.next
                else:
                    previous_node.next = node_.next
                self._len -= 1
                return
            previous_node = node_
            node_ = node_.next

    def hash(self, key: object) -> int:
        """Compute the bucket index for a key.

        Args:
            key: The key to hash.

        Returns:
            Bucket index.
        """
        return hash(key) % self.size

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, key: object) -> object | None:
        return self.get(key)

    def __delitem__(self, key: object) -> None:
        return self.del_(key)

    def __setitem__(self, key: object, value: object) -> None:
        self.put(key, value)
