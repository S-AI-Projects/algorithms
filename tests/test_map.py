import unittest

from algorithms.map import (
    HashTable,
    RandomizedSet,
    ResizableHashTable,
    SeparateChainingHashTable,
    is_anagram,
    is_isomorphic,
    longest_palindromic_subsequence,
    word_pattern,
)


class TestHashTable(unittest.TestCase):
    def test_one_entry(self):
        m = HashTable(10)
        m.put(1, "1")
        self.assertEqual("1", m.get(1))

    def test_add_entry_bigger_than_table_size(self):
        m = HashTable(10)
        m.put(11, "1")
        self.assertEqual("1", m.get(11))

    def test_get_none_if_key_missing_and_hash_collision(self):
        m = HashTable(10)
        m.put(1, "1")
        self.assertEqual(None, m.get(11))

    def test_two_entries_with_same_hash(self):
        m = HashTable(10)
        m.put(1, "1")
        m.put(11, "11")
        self.assertEqual("1", m.get(1))
        self.assertEqual("11", m.get(11))

    def test_get_on_full_table_does_halts(self):
        # and does not search forever
        m = HashTable(10)
        for i in range(10, 20):
            m.put(i, i)
        self.assertEqual(None, m.get(1))

    def test_delete_key(self):
        m = HashTable(10)
        for i in range(5):
            m.put(i, i**2)
        m.del_(1)
        self.assertEqual(None, m.get(1))
        self.assertEqual(4, m.get(2))

    def test_delete_key_and_reassign(self):
        m = HashTable(10)
        m.put(1, 1)
        del m[1]
        m.put(1, 2)
        self.assertEqual(2, m.get(1))

    def test_assigning_to_full_table_throws_error(self):
        m = HashTable(3)
        m.put(1, 1)
        m.put(2, 2)
        m.put(3, 3)
        with self.assertRaises(ValueError):
            m.put(4, 4)

    def test_len_trivial(self):
        m = HashTable(10)
        self.assertEqual(0, len(m))
        for i in range(10):
            m.put(i, i)
            self.assertEqual(i + 1, len(m))

    def test_len_after_deletions(self):
        m = HashTable(10)
        m.put(1, 1)
        self.assertEqual(1, len(m))
        m.del_(1)
        self.assertEqual(0, len(m))
        m.put(11, 42)
        self.assertEqual(1, len(m))

    def test_resizable_hash_table(self):
        m = ResizableHashTable()
        self.assertEqual(ResizableHashTable.MIN_SIZE, m.size)
        for i in range(ResizableHashTable.MIN_SIZE):
            m.put(i, "foo")
        self.assertEqual(ResizableHashTable.MIN_SIZE * 2, m.size)
        self.assertEqual("foo", m.get(1))
        self.assertEqual("foo", m.get(3))
        self.assertEqual("foo", m.get(ResizableHashTable.MIN_SIZE - 1))

    def test_fill_up_the_limit(self):
        m = HashTable(10)
        for i in range(10):
            m.put(i, i**2)
        for i in range(10):
            self.assertEqual(i**2, m.get(i))


class TestSeparateChainingHashTable(unittest.TestCase):
    def test_one_entry(self):
        m = SeparateChainingHashTable(10)
        m.put(1, "1")
        self.assertEqual("1", m.get(1))

    def test_two_entries_with_same_hash(self):
        m = SeparateChainingHashTable(10)
        m.put(1, "1")
        m.put(11, "11")
        self.assertEqual("1", m.get(1))
        self.assertEqual("11", m.get(11))

    def test_len_trivial(self):
        m = SeparateChainingHashTable(10)
        self.assertEqual(0, len(m))
        for i in range(10):
            m.put(i, i)
            self.assertEqual(i + 1, len(m))

    def test_len_after_deletions(self):
        m = SeparateChainingHashTable(10)
        m.put(1, 1)
        self.assertEqual(1, len(m))
        m.del_(1)
        self.assertEqual(0, len(m))
        m.put(11, 42)
        self.assertEqual(1, len(m))

    def test_delete_key(self):
        m = SeparateChainingHashTable(10)
        for i in range(5):
            m.put(i, i**2)
        m.del_(1)
        self.assertEqual(None, m.get(1))
        self.assertEqual(4, m.get(2))

    def test_delete_key_and_reassign(self):
        m = SeparateChainingHashTable(10)
        m.put(1, 1)
        del m[1]
        m.put(1, 2)
        self.assertEqual(2, m.get(1))

    def test_add_entry_bigger_than_table_size(self):
        m = SeparateChainingHashTable(10)
        m.put(11, "1")
        self.assertEqual("1", m.get(11))

    def test_get_none_if_key_missing_and_hash_collision(self):
        m = SeparateChainingHashTable(10)
        m.put(1, "1")
        self.assertEqual(None, m.get(11))


class TestWordPattern(unittest.TestCase):
    def test_word_pattern(self):
        self.assertTrue(word_pattern("abba", "dog cat cat dog"))
        self.assertFalse(word_pattern("abba", "dog cat cat fish"))
        self.assertFalse(word_pattern("abba", "dog dog dog dog"))
        self.assertFalse(word_pattern("aaaa", "dog cat cat dog"))


class TestIsSomorphic(unittest.TestCase):
    def test_is_isomorphic(self):
        self.assertTrue(is_isomorphic("egg", "add"))
        self.assertFalse(is_isomorphic("foo", "bar"))
        self.assertTrue(is_isomorphic("paper", "title"))


class TestLongestPalindromicSubsequence(unittest.TestCase):
    def test_longest_palindromic_subsequence_is_correct(self):
        self.assertEqual(3, longest_palindromic_subsequence("BBABCBCAB"))
        self.assertEqual(4, longest_palindromic_subsequence("abbaeae"))
        self.assertEqual(7, longest_palindromic_subsequence("babbbababaa"))
        self.assertEqual(4, longest_palindromic_subsequence("daccandeeja"))

    def test_longest_palindromic_subsequence_is_incorrect(self):
        self.assertNotEqual(4, longest_palindromic_subsequence("BBABCBCAB"))
        self.assertNotEqual(5, longest_palindromic_subsequence("abbaeae"))
        self.assertNotEqual(2, longest_palindromic_subsequence("babbbababaa"))
        self.assertNotEqual(1, longest_palindromic_subsequence("daccandeeja"))


class TestIsAnagram(unittest.TestCase):
    def test_is_anagram(self):
        self.assertTrue(is_anagram("anagram", "nagaram"))
        self.assertFalse(is_anagram("rat", "car"))


class TestRandomizedSetRepeatable(unittest.TestCase):
    """Repeatability, dependency seam, and isolation test suite for RandomizedSet."""

    def test_fixture_and_neighbor_with_explicit_values(self):
        rs = RandomizedSet()
        self.assertTrue(rs.insert(1))
        self.assertFalse(rs.insert(1))

        # Neighbor: insert distinct element 2, remove 1, remove 1 again, get_random
        self.assertTrue(rs.insert(2))
        self.assertTrue(rs.remove(1))
        self.assertFalse(rs.remove(1))
        self.assertEqual(rs.get_random(), 2)

    def test_repeatability_and_input_isolation(self):
        # Run 1: fresh isolated instance
        rs1 = RandomizedSet()
        ops1 = [
            rs1.insert(1),
            rs1.insert(1),
            rs1.insert(2),
            rs1.remove(1),
            rs1.remove(1),
            rs1.get_random(),
        ]

        # Run 2: second fresh isolated instance
        rs2 = RandomizedSet()
        ops2 = [
            rs2.insert(1),
            rs2.insert(1),
            rs2.insert(2),
            rs2.remove(1),
            rs2.remove(1),
            rs2.get_random(),
        ]

        self.assertEqual(ops1, ops2)
        self.assertEqual(ops1, [True, False, True, True, False, 2])

        # Another valid input on separate instance
        rs_other = RandomizedSet()
        rs_other.insert(99)
        rs_other.insert(100)

        # Run 3: after earlier operations on other instances
        rs3 = RandomizedSet()
        ops3 = [
            rs3.insert(1),
            rs3.insert(1),
            rs3.insert(2),
            rs3.remove(1),
            rs3.remove(1),
            rs3.get_random(),
        ]
        self.assertEqual(ops3, ops1)

        # Confirm rs_other is isolated and intact
        self.assertFalse(rs_other.insert(99))
        self.assertTrue(rs_other.remove(99))

    def test_deterministic_dependency_seam(self):
        # Inject deterministic seeded RNGs
        import random

        rng1 = random.Random(42)
        rs1 = RandomizedSet(rng=rng1)
        for val in range(10):
            rs1.insert(val)
        seq1 = [rs1.get_random() for _ in range(20)]

        rng2 = random.Random(42)
        rs2 = RandomizedSet(rng=rng2)
        for val in range(10):
            rs2.insert(val)
        seq2 = [rs2.get_random() for _ in range(20)]

        self.assertEqual(seq1, seq2)

    def test_empty_set_get_random_raises(self):
        rs = RandomizedSet()
        with self.assertRaises(IndexError):
            rs.get_random()


if __name__ == "__main__":
    unittest.main()
