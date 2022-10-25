import unittest
from unittest import mock

from gnosis.eth import EthereumClient, EthereumNetwork

from safe_cli.api.transaction_service_api import TransactionServiceApi


class TestTransactionService(unittest.TestCase):
    def setUp(self) -> None:
        self.ethereum_client = EthereumClient("http://localhost:8545")
        with mock.patch.object(
            EthereumClient, "get_network", return_value=EthereumNetwork.GOERLI
        ):
            self.transaction_service = TransactionServiceApi.from_ethereum_client(
                self.ethereum_client
            )  # Goerli
        self.safe_address = "0x24833C9c4644a70250BCCBcB5f8529b609eaE6EC"

    def test_data_decoded_to_text(self):
        test_data = {
            "method": "multiSend",
            "parameters": [
                {
                    "name": "transactions",
                    "type": "bytes",
                    "value": "0x00c68877b75c3f9b950a798f9c9df4cde121c432ed000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000247de7edef00000000000000000000000034cfac646f301356faa8b21e94227e3583fe3f5f00c68877b75c3f9b950a798f9c9df4cde121c432ed00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000024f08a0323000000000000000000000000d5d82b6addc9027b22dca772aa68d5d74cdbdf44",
                    "decodedValue": [
                        {
                            "operation": "CALL",
                            "to": "0xc68877B75c3f9b950a798f9C9dF4cDE121C432eD",
                            "value": 0,
                            "data": "0x7de7edef00000000000000000000000034cfac646f301356faa8b21e94227e3583fe3f5f",
                            "decodedData": {
                                "method": "changeMasterCopy",
                                "parameters": [
                                    {
                                        "name": "_masterCopy",
                                        "type": "address",
                                        "value": "0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F",
                                    }
                                ],
                            },
                        },
                        {
                            "operation": "CALL",
                            "to": "0xc68877B75c3f9b950a798f9C9dF4cDE121C432eD",
                            "value": 0,
                            "data": "0xf08a0323000000000000000000000000d5d82b6addc9027b22dca772aa68d5d74cdbdf44",
                            "decodedData": {
                                "method": "setFallbackHandler",
                                "parameters": [
                                    {
                                        "name": "handler",
                                        "type": "address",
                                        "value": "0xd5D82B6aDDc9027B22dCA772Aa68D5d74cdBdF44",
                                    }
                                ],
                            },
                        },
                    ],
                }
            ],
        }
        decoded_data_text = self.transaction_service.data_decoded_to_text(test_data)
        self.assertIn(
            "- changeMasterCopy: 0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F",
            decoded_data_text,
        )
        self.assertIn(
            "- setFallbackHandler: 0xd5D82B6aDDc9027B22dCA772Aa68D5d74cdBdF44",
            decoded_data_text,
        )

    def test_get_balances(self):
        balances = self.transaction_service.get_balances(self.safe_address)
        self.assertIsInstance(balances, list)

    def test_get_transactions(self):
        transactions = self.transaction_service.get_transactions(self.safe_address)
        self.assertIsInstance(transactions, list)


if __name__ == "__main__":
    unittest.main()
