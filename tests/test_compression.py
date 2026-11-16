import unittest

from algorithms.compression.elias import elias_delta, elias_gamma
from algorithms.compression.huffman_coding import HuffmanCoding, Node
from algorithms.compression.lzw_compression import lzw_decode, lzw_encode
from algorithms.compression.rle_compression import decode_rle, encode_rle


class TestHuffmanCoding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_in_name = "huffman_coding_in.txt"
        cls.file_out_bin_name = "huffman_coding_out.bin"
        cls.file_out_name = "huffman_coding_out.txt"

    def setUp(self):
        import random

        random.seed(1951)
        with open(self.file_in_name, "wb") as file_in:
            for _ in range(10000):
                file_in.write(bytes([random.randrange(0, 256)]))

    def test_huffman_coding(self):
        HuffmanCoding.encode_file(self.file_in_name, self.file_out_bin_name)
        HuffmanCoding.decode_file(self.file_out_bin_name, self.file_out_name)

        with (
            open(self.file_in_name, "rb") as file_1,
            open(self.file_out_name, "rb") as file_2,
        ):
            content_1 = file_1.read()
            content_2 = file_2.read()

            self.assertEqual(content_1, content_2)

    def tearDown(self):
        import os

        os.remove(self.file_in_name)
        os.remove(self.file_out_bin_name)
        os.remove(self.file_out_name)


class TestHuffmanNode(unittest.TestCase):
    """Public contract of Node in huffman_coding.py.

    Written before refactoring Node, with expected values worked out by hand
    from the source: defaults (L26-29), ordering by frequency (L36-40),
    equality by frequency only (L42-45) and the text form
    ``<ch: {sign}: {frequency}>`` (L47-51, at commit bd1d152).
    """

    def test_smallest_valid_input_uses_the_defaults(self):
        node = Node()
        self.assertEqual(0, node.frequency)
        self.assertIsNone(node.sign)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertEqual("<ch: None: 0>", str(node))
        self.assertEqual("<ch: None: 0>", repr(node))

    def test_ordinary_leaf(self):
        leaf = Node(frequency=5, sign=97)
        self.assertEqual(5, leaf.frequency)
        self.assertEqual(97, leaf.sign)
        self.assertIsNone(leaf.left)
        self.assertIsNone(leaf.right)
        self.assertEqual("<ch: 97: 5>", str(leaf))
        self.assertEqual("<ch: 97: 5>", repr(leaf))

    def test_ordinary_internal_node(self):
        left = Node(frequency=2, sign=98)
        right = Node(frequency=3, sign=99)
        parent = Node(frequency=5, left=left, right=right)
        self.assertIs(left, parent.left)
        self.assertIs(right, parent.right)
        self.assertIsNone(parent.sign)
        self.assertEqual("<ch: None: 5>", str(parent))
        self.assertEqual("<ch: None: 5>", repr(parent))
        # Containers show their items with repr().
        self.assertEqual("[<ch: 98: 2>, <ch: 99: 3>]", str([left, right]))

    def test_ordering_and_equality_use_frequency_only(self):
        low = Node(frequency=2, sign=1)
        high = Node(frequency=7, sign=2)
        self.assertIs(True, low < high)
        self.assertIs(False, high < low)
        self.assertIs(True, high > low)
        self.assertIs(False, low > high)
        self.assertIs(True, Node(frequency=4, sign=1) == Node(frequency=4, sign=2))
        self.assertIs(False, Node(frequency=4) == Node(frequency=5))
        # A non-Node is never equal: __eq__ returns NotImplemented (L43-44).
        self.assertIs(False, Node(frequency=4) == 4)


class TestRLECompression(unittest.TestCase):
    def test_encode_rle(self):
        self.assertEqual(
            "12W1B12W3B24W1B14W",
            encode_rle(
                "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"
            ),
        )

    def test_decode_rle(self):
        self.assertEqual(
            "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW",
            decode_rle("12W1B12W3B24W1B14W"),
        )


class TestEliasCoding(unittest.TestCase):
    def test_elias_gamma(self):
        correct_result = [
            "1",
            "010",
            "011",
            "00100",
            "00101",
            "00110",
            "00111",
            "0001000",
            "0001001",
            "0001010",
        ]

        result = [elias_gamma(i) for i in range(1, 11)]

        self.assertEqual(correct_result, result)
        with self.assertRaises(ValueError):
            elias_gamma(0)

    def test_elias_delta(self):
        correct_result = [
            "1",
            "0100",
            "0101",
            "01100",
            "01101",
            "01110",
            "01111",
            "00100000",
            "00100001",
            "00100010",
        ]

        result = [elias_delta(i) for i in range(1, 11)]

        self.assertEqual(correct_result, result)
        with self.assertRaises(ValueError):
            elias_delta(0)


class TestLZWCompression(unittest.TestCase):
    def test_lzw_encode(self):
        codes, dictionary = lzw_encode("ABABABA")
        self.assertEqual([0, 1, 2, 4], codes)
        self.assertEqual({0: "A", 1: "B"}, dictionary)

    def test_lzw_decode(self):
        self.assertEqual("ABABABA", lzw_decode([0, 1, 2, 4], {0: "A", 1: "B"}))

    def test_lzw_roundtrip(self):
        data = "TOBEORNOTTOBEORTOBEORNOT"
        encoded, dictionary = lzw_encode(data)
        decoded = lzw_decode(encoded, dictionary)
        self.assertEqual(data, decoded)

    def test_lzw_empty(self):
        self.assertEqual(([], {}), lzw_encode(""))
        self.assertEqual("", lzw_decode([], {}))


if __name__ == "__main__":
    unittest.main()
