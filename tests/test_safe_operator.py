import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from ledgereth.objects import LedgerAccount
from web3 import Web3

from gnosis.eth import EthereumClient
from gnosis.safe import Safe
from gnosis.safe.multi_send import MultiSend

from safe_cli.operators.safe_operator import (
    AccountNotLoadedException,
    ExistingOwnerException,
    FallbackHandlerNotSupportedException,
    GuardNotSupportedException,
    HashAlreadyApproved,
    InvalidFallbackHandlerException,
    InvalidGuardException,
    InvalidMasterCopyException,
    NonExistingOwnerException,
    NotEnoughEtherToSend,
    NotEnoughSignatures,
    SafeOperator,
    SameFallbackHandlerException,
    SameGuardException,
    SameMasterCopyException,
    SenderRequiredException,
)
from safe_cli.utils import get_erc_20_list
from tests.utils import generate_transfers_erc20

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeOperator(SafeCliTestCaseMixin, unittest.TestCase):
    def test_setup_operator(self):
        for number_owners in range(1, 4):
            safe_operator = self.setup_operator(number_owners=number_owners)
            self.assertEqual(len(safe_operator.accounts), number_owners)
            safe = Safe(safe_operator.address, self.ethereum_client)
            self.assertEqual(len(safe.retrieve_owners()), number_owners)

    @mock.patch(
        "gnosis.safe.Safe.contract", new_callable=mock.PropertyMock, return_value=None
    )
    def test_load_cli_owner(self, get_contract_mock: MagicMock):
        random_address = Account.create().address
        safe_operator = SafeOperator(random_address, self.ethereum_node_url)
        random_accounts = [Account.create() for _ in range(3)]
        random_accounts_keys = [account.key.hex() for account in random_accounts]
        self.assertFalse(safe_operator.accounts)
        safe_operator.load_cli_owners(random_accounts_keys)
        self.assertEqual(len(safe_operator.accounts), len(random_accounts_keys))
        # Test accounts are not duplicated
        safe_operator.load_cli_owners(random_accounts_keys)
        self.assertEqual(len(safe_operator.accounts), len(random_accounts_keys))
        # Test invalid accounts don't make the method break
        safe_operator.load_cli_owners(["aloha", Account.create().key.hex(), "bye"])
        self.assertEqual(len(safe_operator.accounts), len(random_accounts_keys) + 1)
        # TODO Test setting default sender, mock getBalance

        # Test unload cli owner
        safe_operator.default_sender = random_accounts[0]
        number_of_accounts = len(safe_operator.accounts)
        safe_operator.unload_cli_owners(["aloha", random_accounts[0].address, "bye"])
        self.assertEqual(len(safe_operator.accounts), number_of_accounts - 1)
        self.assertFalse(safe_operator.default_sender)

    @mock.patch("safe_cli.operators.hw_accounts.ledger_manager.get_account_by_path")
    def test_load_ledger_cli_owner(self, mock_get_account_by_path: MagicMock):
        owner_address = Account.create().address
        safe_address = self.deploy_test_safe(owners=[owner_address]).address
        safe_operator = SafeOperator(safe_address, self.ethereum_node_url)
        safe_operator.ledger_manager.get_accounts = MagicMock(return_value=[])
        safe_operator.load_ledger_cli_owners()
        self.assertEqual(len(safe_operator.ledger_manager.accounts), 0)
        random_account = Account.create().address
        other_random_account = Account.create().address
        safe_operator.ledger_manager.get_accounts.return_value = [
            (random_account, "44'/60'/0'/0/0"),
            (other_random_account, "44'/60'/0'/0/1"),
        ]
        mock_get_account_by_path.return_value = LedgerAccount(
            "44'/60'/0'/0/0", random_account
        )
        safe_operator.load_ledger_cli_owners()
        self.assertEqual(len(safe_operator.ledger_manager.accounts), 1)

    def test_approve_hash(self):
        safe_address = self.deploy_test_safe(
            owners=[self.ethereum_test_account.address]
        ).address
        safe_operator = SafeOperator(safe_address, self.ethereum_node_url)
        safe_tx_hash = Web3.keccak(text="random-test")
        random_account = Account.create()
        with self.assertRaises(AccountNotLoadedException):
            safe_operator.approve_hash(safe_tx_hash, random_account.address)

        with self.assertRaises(NonExistingOwnerException):
            safe_operator.accounts.add(random_account)
            safe_operator.approve_hash(safe_tx_hash, random_account.address)

        safe_operator.accounts.add(self.ethereum_test_account)
        safe_operator.default_sender = self.ethereum_test_account
        self.assertTrue(
            safe_operator.approve_hash(safe_tx_hash, self.ethereum_test_account.address)
        )
        with self.assertRaises(HashAlreadyApproved):
            safe_operator.approve_hash(safe_tx_hash, self.ethereum_test_account.address)

    def test_add_owner(self):
        safe_address = self.deploy_test_safe(
            owners=[self.ethereum_test_account.address]
        ).address
        safe_operator = SafeOperator(safe_address, self.ethereum_node_url)
        with self.assertRaises(ExistingOwnerException):
            safe_operator.add_owner(self.ethereum_test_account.address)

        new_owner = Account.create().address
        with self.assertRaises(NotEnoughSignatures):
            safe_operator.add_owner(new_owner)

        safe_operator.accounts.add(self.ethereum_test_account)

        with self.assertRaises(SenderRequiredException):
            safe_operator.add_owner(new_owner)

        safe_operator.default_sender = self.ethereum_test_account

        safe = Safe(safe_address, self.ethereum_client)
        self.assertTrue(safe_operator.add_owner(new_owner))
        self.assertIn(self.ethereum_test_account, safe_operator.accounts)
        self.assertIn(new_owner, safe.retrieve_owners())

    def test_remove_owner(self):
        safe_address = self.deploy_test_safe(
            owners=[self.ethereum_test_account.address]
        ).address
        safe_operator = SafeOperator(safe_address, self.ethereum_node_url)
        random_address = Account.create().address
        with self.assertRaises(NonExistingOwnerException):
            safe_operator.remove_owner(random_address)

        safe_operator.load_cli_owners([self.ethereum_test_account.key.hex()])
        new_owner = Account.create().address
        safe = Safe(safe_address, self.ethereum_client)
        self.assertTrue(safe_operator.add_owner(new_owner))
        self.assertIn(new_owner, safe.retrieve_owners())

        self.assertTrue(safe_operator.remove_owner(new_owner))
        self.assertNotIn(new_owner, safe_operator.accounts)
        self.assertNotIn(new_owner, safe.retrieve_owners())

    def test_change_fallback_handler(self):
        safe_operator = self.setup_operator()
        safe = Safe(safe_operator.address, self.ethereum_client)
        current_fallback_handler = safe.retrieve_fallback_handler()
        with self.assertRaises(SameFallbackHandlerException):
            safe_operator.change_fallback_handler(current_fallback_handler)

        new_fallback_handler = Account.create().address
        with self.assertRaises(InvalidFallbackHandlerException):
            # Contract does not exist
            self.assertTrue(safe_operator.change_fallback_handler(new_fallback_handler))

        with mock.patch.object(
            EthereumClient, "is_contract", autospec=True, return_value=True
        ):
            self.assertTrue(safe_operator.change_fallback_handler(new_fallback_handler))
        self.assertEqual(
            safe_operator.safe_cli_info.fallback_handler, new_fallback_handler
        )
        self.assertEqual(safe.retrieve_fallback_handler(), new_fallback_handler)

        # Safes < 1.1.0 don't support the fallback handler
        safe_operator_v1_0_0 = self.setup_operator(version="1.0.0")
        with self.assertRaises(FallbackHandlerNotSupportedException):
            safe_operator_v1_0_0.change_fallback_handler(Account.create().address)

    def test_change_guard(self):
        safe_operator = self.setup_operator(version="1.1.1")
        with self.assertRaises(GuardNotSupportedException):
            safe_operator.change_guard(Account.create().address)

        safe_operator = self.setup_operator(version="1.4.1")
        safe = Safe(safe_operator.address, self.ethereum_client)
        current_guard = safe.retrieve_guard()
        with self.assertRaises(SameGuardException):
            safe_operator.change_guard(current_guard)

        not_valid_guard = Account.create().address
        with self.assertRaises(InvalidGuardException):  # Contract does not exist
            self.assertTrue(safe_operator.change_guard(not_valid_guard))

        new_guard = self.deploy_example_guard()
        self.assertTrue(safe_operator.change_guard(new_guard))
        self.assertEqual(safe_operator.safe_cli_info.guard, new_guard)
        self.assertEqual(safe.retrieve_guard(), new_guard)

    def test_change_master_copy(self):
        safe_operator = self.setup_operator(version="1.1.1")
        safe = Safe(safe_operator.address, self.ethereum_client)
        current_master_copy = safe.retrieve_master_copy_address()
        self.assertEqual(current_master_copy, self.safe_contract_V1_1_1.address)
        with self.assertRaises(SameMasterCopyException):
            safe_operator.change_master_copy(current_master_copy)

        random_address = Account.create().address
        with self.assertRaises(InvalidMasterCopyException):
            safe_operator.change_master_copy(random_address)

        new_master_copy = self.safe_contract_V1_3_0.address
        self.assertTrue(safe_operator.change_master_copy(new_master_copy))
        self.assertEqual(safe_operator.safe_cli_info.master_copy, new_master_copy)
        self.assertEqual(safe.retrieve_master_copy_address(), new_master_copy)

    def test_send_ether(self):
        safe_operator = self.setup_operator()
        random_address = Account.create().address
        value = 123
        with self.assertRaises(NotEnoughEtherToSend):
            safe_operator.send_ether(random_address, value)
        self.ethereum_client.send_eth_to(
            self.ethereum_test_account.key,
            safe_operator.address,
            self.w3.eth.gas_price,
            value * 2,
            gas=50000,
        )
        self.assertEqual(
            self.ethereum_client.get_balance(safe_operator.address), value * 2
        )
        self.assertTrue(safe_operator.send_ether(random_address, value))
        self.assertEqual(self.ethereum_client.get_balance(random_address), value)

    def test_drain(self):
        safe_operator = self.setup_operator()
        account = Account.create()
        value = self.w3.to_wei(10.5, "ether")

        with self.assertRaises(NotEnoughEtherToSend):
            safe_operator.send_ether(account.address, value)

        self.ethereum_client.send_eth_to(
            self.ethereum_test_account.key,
            safe_operator.address,
            self.w3.eth.gas_price,
            value,
            gas=50000,
        )
        safe_operator.send_ether(account.address, value - 5)
        # Deploying 3 contracts and sending 3 transactions of 1 ERC20 per contract
        num_transactions = 3
        num_contracts_erc20 = 3
        generate_transfers_erc20(
            self.w3, safe_operator, account, num_contracts_erc20, num_transactions
        )
        # Deploying multisend contract on ganache
        _, _, contract_address = MultiSend.deploy_contract(
            self.ethereum_client, account
        )
        with mock.patch.object(
            MultiSend, "MULTISEND_CALL_ONLY_ADDRESSES", [contract_address]
        ):
            # Getting events filtered by Transfer
            last = safe_operator.ethereum_client.get_block("latest")["number"]
            token_address = get_erc_20_list(
                safe_operator.ethereum_client, safe_operator.address, 1, last
            )
            self.assertEqual(len(token_address), num_contracts_erc20)
            for token in token_address:
                result = self.ethereum_client.erc20.get_balance(
                    safe_operator.address, token
                )
                self.assertEqual(result, num_transactions)
            # Draining the account to a new account
            safe_operator.drain(account.address)
            # Checking that the account is empty
            for token in token_address:
                self.assertEqual(
                    self.ethereum_client.erc20.get_balance(
                        safe_operator.address, token
                    ),
                    0,
                )
            self.assertEqual(
                safe_operator.ethereum_client.get_balance(safe_operator.address), 0
            )


if __name__ == "__main__":
    unittest.main()
