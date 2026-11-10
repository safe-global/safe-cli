import argparse
import unittest

from safe_cli.argparse_validators import check_positive_integer


class TestCheckPositiveIntegerEdgeCases(unittest.TestCase):
    def test_non_numeric_string_raises_argument_type_error(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive_integer("abc")

    def test_none_raises_argument_type_error(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive_integer(None)

    def test_valid_values_still_accepted(self):
        self.assertEqual(check_positive_integer("3"), 3)
        self.assertEqual(check_positive_integer(1), 1)

    def test_zero_and_negative_still_rejected(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive_integer("0")
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive_integer("-2")


if __name__ == "__main__":
    unittest.main()
