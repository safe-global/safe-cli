import os
import unittest
from unittest import mock
from unittest.mock import MagicMock

import pytest
from eth_account import Account
from eth_typing import HexStr
from typer.testing import CliRunner

from gnosis.eth import EthereumClient
from gnosis.eth.constants import NULL_ADDRESS
from gnosis.safe import Safe
from gnosis.safe.api import TransactionServiceApi
from gnosis.safe.safe import SafeInfo

from safe_cli import VERSION
from safe_cli.main import app
from safe_cli.operators.exceptions import (
    NotEnoughEtherToSend,
    SafeOperatorException,
    SenderRequiredException,
)
from safe_cli.safe_cli import SafeCli

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin

runner = CliRunner()


class TestSafeCliEntryPoint(SafeCliTestCaseMixin, unittest.TestCase):
    random_safe_address = Account.create().address

    def test_version(self):
        result = runner.invoke(app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(f"Safe Cli v{VERSION}", result.stdout)

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

        # Test key from env
        os.environ["random_key"] = safe_owner.key.hex()
        result = runner.invoke(
            app,
            [
                "send-ether",
                safe_operator.safe.address,
                "http://localhost:8545",
                random_address,
                "20",
                "--private-key",
                "random_key",
            ],
        )
        self.assertEqual(result.exit_code, 0)

        # Test interactive/non-interactive mode
        del os.environ["PYTEST_CURRENT_TEST"]  # To avoid skip yes/no question
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
        self.assertEqual(result.exit_code, 1)

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
                "--non-interactive",
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

    def test_tx_builder(self):
        safe_operator = self.setup_operator()
        safe_owner = Account.create()
        safe_operator.add_owner(safe_owner.address, 1)
        self._send_eth_to(safe_owner.address, 1000000000000000000)

        # Test exit code 1 with empty file
        result = runner.invoke(
            app,
            [
                "tx-builder",
                safe_operator.safe.address,
                "http://localhost:8545",
                "tests/mocks/tx_builder/empty_txs.json",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        self.assertEqual(result.exit_code, 2)

        # Test single tx exit 0
        result = runner.invoke(
            app,
            [
                "tx-builder",
                safe_operator.safe.address,
                "http://localhost:8545",
                "tests/mocks/tx_builder/single_tx.json",
                "--private-key",
                safe_owner.key.hex(),
            ],
        )
        self.assertEqual(result.exit_code, 0)

        # Test batch txs (Ends with exception because the multisend contract is not deployed.)
        result = runner.invoke(
            app,
            [
                "tx-builder",
                safe_operator.safe.address,
                "http://localhost:8545",
                "tests/mocks/tx_builder/batch_txs.json",
                "--private-key",
                safe_owner.key.hex(),
                "--non-interactive",
            ],
        )
        exception, _, _ = result.exc_info
        self.assertEqual(exception, SafeOperatorException)
        self.assertEqual(result.exit_code, 1)

    def _send_eth_to(self, address: str, value: int) -> None:
        self.ethereum_client.send_eth_to(
            self.ethereum_test_account.key,
            address,
            self.w3.eth.gas_price,
            value,
            gas=50000,
        )

    @mock.patch.object(Safe, "retrieve_all_info")
    def test_build_safe_cli(self, retrieve_all_info_mock: MagicMock):
        safe_owner = Account.create().address
        retrieve_all_info_mock.return_value = SafeInfo(
            self.random_safe_address,
            "0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99",
            NULL_ADDRESS,
            "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762",
            [],
            0,
            [safe_owner],
            1,
            "1.4.1",
        )
        result = runner.invoke(
            app,
            [
                "attended-mode",
                self.random_safe_address,
                "http://localhost:8545",
                "--history",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @mock.patch.object(EthereumClient, "get_chain_id", return_value=5)
    @mock.patch.object(TransactionServiceApi, "get_safes_for_owner")
    @mock.patch.object(Safe, "retrieve_all_info")
    def test_build_safe_cli_for_owner(
        self,
        retrieve_all_info_mock: MagicMock,
        get_safes_for_owner_mock: MagicMock,
        get_chain_id_mock: MagicMock,
    ):
        safe_owner = Account.create().address
        retrieve_all_info_mock.return_value = SafeInfo(
            self.random_safe_address,
            "0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99",
            NULL_ADDRESS,
            "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762",
            [],
            0,
            [safe_owner],
            1,
            "1.4.1",
        )
        get_safes_for_owner_mock.return_value = []

        result = runner.invoke(
            app,
            [
                "attended-mode",
                safe_owner,
                "http://localhost:8545",
                "--history",
                "--get-safes-from-owner",
            ],
            input="",
        )
        exception, _, _ = result.exc_info
        self.assertEqual(exception, ValueError)
        self.assertEqual(result.exit_code, 1)

    @mock.patch.object(Safe, "retrieve_all_info")
    @mock.patch.object(SafeCli, "get_command")
    def test_parse_operator_mode(
        self, get_command_mock: MagicMock, retrieve_all_info_mock: MagicMock
    ):
        safe_owner = Account.create().address
        retrieve_all_info_mock.return_value = SafeInfo(
            self.random_safe_address,
            "0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99",
            NULL_ADDRESS,
            "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762",
            [],
            0,
            [safe_owner],
            1,
            "1.4.1",
        )
        get_command_mock.side_effect = ["tx-service", "exit"]

        result = runner.invoke(
            app,
            [
                "attended-mode",
                self.random_safe_address,
                "http://localhost:8545",
                "--history",
            ],
        )

        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    pytest.main()
