import unittest

from eth_account import Account
from eth_typing import HexStr
from typer.testing import CliRunner

from safe_cli import VERSION
from safe_cli.operators.exceptions import NotEnoughEtherToSend, SenderRequiredException
from safe_cli.safe_runner import app

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin

runner = CliRunner()


class TestSafeRunner(SafeCliTestCaseMixin, unittest.TestCase):

    def test_version(self):
        result = runner.invoke(app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(f"Safe Runner v{VERSION}", result.stdout)

    def test_send_ether(self):
        safe_operator = self.setup_operator()
        safe_owner = Account.create()
        safe_operator.add_owner(safe_owner.address, 1)
        random_address = Account.create().address

        # Test exception with exit code 1
        result = runner.invoke(
            app,
            [
                "send-ether",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                "20",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        exception, _, _ = result.exc_info
        self.assertEqual(exception, NotEnoughEtherToSend)
        self.assertEqual(result.exit_code, 1)

        # Test exit code 0
        self._send_eth_to(safe_owner.address, 1000000000000000000)
        self._send_eth_to(safe_operator.safe.address, 1000000000000000000)
        result = runner.invoke(
            app,
            [
                "send-ether",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                "20",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        self.assertEqual(result.exit_code, 0)

    def test_send_erc20(self):
        safe_operator = self.setup_operator()
        safe_owner = Account.create()
        safe_operator.add_owner(safe_owner.address, 1)

        random_address = Account.create().address
        random_token_address = Account.create().address

        # Test exception with exit code 1
        result = runner.invoke(
            app,
            [
                "send-erc20",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                random_token_address,
                "20",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        exception, _, _ = result.exc_info
        self.assertEqual(exception, SenderRequiredException)
        self.assertEqual(result.exit_code, 1)

        # Test exit code 0. Add user as a default signer
        self._send_eth_to(safe_owner.address, 1000000000000000000)

        result = runner.invoke(
            app,
            [
                "send-erc20",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                random_token_address,
                "20",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        self.assertEqual(result.exit_code, 0)

    def test_send_erc721(self):
        safe_operator = self.setup_operator()
        safe_owner = Account.create()
        safe_operator.add_owner(safe_owner.address, 1)

        random_address = Account.create().address
        random_token_address = Account.create().address

        # Test exception with exit code 1
        result = runner.invoke(
            app,
            [
                "send-erc721",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                random_token_address,
                "1",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        exception, _, _ = result.exc_info
        self.assertEqual(exception, SenderRequiredException)
        self.assertEqual(result.exit_code, 1)

        # Test exit code 0. Add user as a default signer
        self._send_eth_to(safe_owner.address, 1000000000000000000)

        result = runner.invoke(
            app,
            [
                "send-erc721",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                random_token_address,
                "1",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        self.assertEqual(result.exit_code, 0)

    def test_send_custom(self):
        safe_operator = self.setup_operator()
        safe_owner = Account.create()
        safe_operator.add_owner(safe_owner.address, 1)

        random_address = Account.create().address
        data = HexStr(
            "0xa9059cbb00000000000000000000000079500008b4ea3cc3ad391145dca8a11bc04962280000000000000000000000000000000000000000000000000de0b6b3a7640000"
        )

        # Test exception with exit code 1
        result = runner.invoke(
            app,
            [
                "send-custom",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                "0",
                data,
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        exception, _, _ = result.exc_info
        self.assertEqual(exception, SenderRequiredException)
        self.assertEqual(result.exit_code, 1)

        # Test exit code 0. Add user as a default signer
        self._send_eth_to(safe_owner.address, 1000000000000000000)

        result = runner.invoke(
            app,
            [
                "send-custom",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                "0",
                data,
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        self.assertEqual(result.exit_code, 0)

    def _send_eth_to(self, address: str, value: int) -> None:
        self.ethereum_client.send_eth_to(
            self.ethereum_test_account.key,
            address,
            self.w3.eth.gas_price,
            value,
            gas=50000,
        )


if __name__ == "__main__":
    unittest.main()
