import math
import sys
import unittest
from pathlib import Path

# Ensure src directory is importable when running tests without installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from userverse_python_client import add_numbers, subtract_numbers


class TestArithmetic(unittest.TestCase):
    def test_add_numbers(self) -> None:
        cases = (
            (1, 2, 3),
            (-1, 1, 0),
            (2.5, 3.1, 5.6),
        )
        for first, second, expected in cases:
            with self.subTest(first=first, second=second):
                self.assertTrue(math.isclose(add_numbers(first, second), expected))

    def test_subtract_numbers(self) -> None:
        cases = (
            (1, 2, -1),
            (-1, 1, -2),
            (2.5, 3.1, -0.6),
        )
        for first, second, expected in cases:
            with self.subTest(first=first, second=second):
                self.assertTrue(math.isclose(subtract_numbers(first, second), expected))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
