import os
import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account

from safe_cli.utils import choose_option_from_list_question, yes_or_no_question


class TestUtils(unittest.TestCase):
    @mock.patch("safe_cli.utils.get_input")
    def test_yes_or_no_question(self, input_mock: MagicMock):
        # Input defaults to `yes` if running tests
        pytest_current_test = os.environ.pop("PYTEST_CURRENT_TEST")
        input_mock.return_value = "yes"
        self.assertTrue(yes_or_no_question(""))

        input_mock.return_value = "yay"
        self.assertTrue(yes_or_no_question(""))

        input_mock.return_value = "Y"
        self.assertTrue(yes_or_no_question(""))

        input_mock.return_value = "Nope"
        self.assertFalse(yes_or_no_question(""))

        input_mock.return_value = "No"
        self.assertFalse(yes_or_no_question(""))

        input_mock.return_value = "n"
        self.assertFalse(yes_or_no_question(""))

        input_mock.return_value = "random"
        self.assertFalse(yes_or_no_question(""))

        os.environ["PYTEST_CURRENT_TEST"] = pytest_current_test

    @mock.patch("safe_cli.utils.get_input")
    def test_choose_option_question(self, input_mock: MagicMock):
        pytest_current_test = os.environ.pop("PYTEST_CURRENT_TEST")
        address = Account.create().address
        options = [address for i in range(0, 5)]
        input_mock.return_value = ""
        self.assertEqual(choose_option_from_list_question("", options), 0)
        input_mock.return_value = ""
        self.assertEqual(choose_option_from_list_question("", options, 4), 4)
        input_mock.return_value = "m"
        self.assertIsNone(choose_option_from_list_question("", options))
        input_mock.return_value = "10"
        self.assertIsNone(choose_option_from_list_question("", options))
        input_mock.return_value = "1"
        self.assertEqual(choose_option_from_list_question("", options), 1)

        os.environ["PYTEST_CURRENT_TEST"] = pytest_current_test


if __name__ == "__main__":
    unittest.main()
