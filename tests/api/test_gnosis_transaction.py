import unittest

from safe_cli.api.gnosis_transaction import TransactionService


class TestTransactionService(unittest.TestCase):
    def setUp(self) -> None:
        self.transaction_service = TransactionService.from_network_number(4)  # Rinkeby
        self.safe_address = '0x7552Ed65a45E27740a15B8D5415E90d8ca64C109'

    def test_get_balances(self):
        balances = self.transaction_service.get_balances(self.safe_address)
        self.assertIsInstance(balances, list)

    def test_get_transactions(self):
        transactions = self.transaction_service.get_transactions(self.safe_address)
        self.assertIsInstance(transactions, list)


if __name__ == '__main__':
    unittest.main()
