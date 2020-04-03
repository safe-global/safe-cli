import os
import unittest

from eth_account import Account
from safe_operator import SafeOperator

ETHEREUM_NODE_URL = os.environ.get('ETHEREUM_NODE_URL', 'http://localhost:8545')


class SafeCliTestCase(unittest.TestCase):
    def test_send_erc20(self):
        random_address = Account.create().address
        with self.assertRaises(ValueError):
            safe_operator = SafeOperator(random_address, ETHEREUM_NODE_URL)
            safe_operator.send_erc20(Account.create().address, Account.create().address, 0)


if __name__ == '__main__':
    unittest.main()
