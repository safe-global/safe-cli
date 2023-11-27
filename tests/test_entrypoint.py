import argparse
import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from prompt_toolkit import HTML

from gnosis.eth.constants import NULL_ADDRESS
from gnosis.eth.ethereum_client import EthereumClient
from gnosis.safe import Safe
from gnosis.safe.api import TransactionServiceApi
from gnosis.safe.safe import SafeInfo

from safe_cli.main import SafeCli, build_safe_cli
from safe_cli.operators import SafeOperator

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class SafeCliEntrypointTestCase(SafeCliTestCaseMixin, unittest.TestCase):
    random_safe_address = Account.create().address

    @mock.patch("argparse.ArgumentParser.parse_args")
    def build_test_safe_cli(self, mock_parse_args: MagicMock):
        mock_parse_args.return_value = argparse.Namespace(
            address=self.random_safe_address,
            node_url=self.ethereum_node_url,
            history=True,
            get_safes_from_owner=False,
        )
        return build_safe_cli()

    @mock.patch("argparse.ArgumentParser.parse_args")
    def build_test_safe_cli_for_owner(self, mock_parse_args: MagicMock):
        mock_parse_args.return_value = argparse.Namespace(
            address=self.random_safe_address,
            node_url=self.ethereum_node_url,
            history=True,
            get_safes_from_owner=True,
        )
        return build_safe_cli()

    @mock.patch.object(Safe, "retrieve_all_info")
    def test_build_safe_cli(self, retrieve_all_info_mock: MagicMock):
        retrieve_all_info_mock.return_value = SafeInfo(
            self.random_safe_address,
            "0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99",
            NULL_ADDRESS,
            "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762",
            [],
            0,
            [Account.create().address],
            1,
            "1.4.1",
        )

        safe_cli = self.build_test_safe_cli()
        with mock.patch.object(SafeOperator, "is_version_updated", return_value=True):
            self.assertIsNone(safe_cli.print_startup_info())
        self.assertIsInstance(safe_cli.get_prompt_text(), HTML)
        self.assertIsInstance(safe_cli.get_bottom_toolbar(), HTML)

    @mock.patch.object(EthereumClient, "get_chain_id", return_value=5)
    @mock.patch.object(TransactionServiceApi, "get_safes_for_owner")
    @mock.patch.object(Safe, "retrieve_all_info")
    def test_build_safe_cli_for_owner(
        self,
        retrieve_all_info_mock: MagicMock,
        get_safes_for_owner_mock: MagicMock,
        get_chain_id_mock: MagicMock,
    ):
        retrieve_all_info_mock.return_value = SafeInfo(
            self.random_safe_address,
            "0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99",
            NULL_ADDRESS,
            "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762",
            [],
            0,
            [Account.create().address],
            1,
            "1.4.1",
        )
        get_safes_for_owner_mock.return_value = []
        with self.assertRaises(ValueError):
            self.build_test_safe_cli_for_owner()
        get_safes_for_owner_mock.return_value = [self.random_safe_address]
        safe_cli = self.build_test_safe_cli_for_owner()
        self.assertIsNotNone(safe_cli)
        with mock.patch.object(SafeOperator, "is_version_updated", return_value=True):
            self.assertIsNone(safe_cli.print_startup_info())
        self.assertIsInstance(safe_cli.get_prompt_text(), HTML)
        self.assertIsInstance(safe_cli.get_bottom_toolbar(), HTML)

    def test_parse_operator_mode(self):
        safe_cli = self.build_test_safe_cli()
        self.assertIsNone(safe_cli.parse_operator_mode("tx-service"))
        self.assertIsInstance(safe_cli.parse_operator_mode("blockchain"), SafeOperator)

    @mock.patch.object(SafeCli, "get_command", side_effect=EOFError)
    def test_loop(self, mock_parse_args: MagicMock):
        safe_cli = self.build_test_safe_cli()
        safe_cli.loop()


if __name__ == "__main__":
    unittest.main()
