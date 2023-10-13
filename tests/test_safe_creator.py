import unittest

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeCreator(SafeCliTestCaseMixin, unittest.TestCase):
    def test_main(self):
        pass


if __name__ == "__main__":
    unittest.main()
