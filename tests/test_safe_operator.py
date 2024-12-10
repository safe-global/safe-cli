import json
import unittest
from functools import lru_cache
from unittest import mock
from unittest.mock import MagicMock, PropertyMock

from eth_account import Account
from eth_typing import ChecksumAddress
from ledgerblue.Dongle import Dongle
from ledgereth.objects import LedgerAccount
from safe_eth.eth import EthereumClient
from safe_eth.eth.eip712 import eip712_encode
from safe_eth.safe import Safe
from safe_eth.safe.multi_send import MultiSend
from web3 import Web3
from web3.types import Wei

from safe_cli.contracts import safe_to_l2_migration
from safe_cli.operators.exceptions import (
    AccountNotLoadedException,
    ExistingOwnerException,
    FallbackHandlerNotSupportedException,
    GuardNotSupportedException,
    HardwareWalletException,
    HashAlreadyApproved,
    InvalidFallbackHandlerException,
    InvalidGuardException,
    InvalidMasterCopyException,
    NonExistingOwnerException,
    NotEnoughEtherToSend,
    NotEnoughSignatures,
    SafeVersionNotSupportedException,
    SameFallbackHandlerException,
    SameGuardException,
    SameMasterCopyException,
    SenderRequiredException,
)
from safe_cli.operators.safe_operator import SafeOperator
from safe_cli.utils import get_erc_20_list
from tests.utils import generate_transfers_erc20

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeOperator(SafeCliTestCaseMixin, unittest.TestCase):
    @lru_cache(maxsize=None)
    def _deploy_l2_migration_contract(self) -> ChecksumAddress:
        # Deploy L2 migration contract
        safe_to_l2_migration_contract = self.w3.eth.contract(
            abi=safe_to_l2_migration["abi"], bytecode=safe_to_l2_migration["bytecode"]
        )
        tx_hash = safe_to_l2_migration_contract.constructor().transact(
            {"from": self.ethereum_test_account.address}
        )
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt["contractAddress"]

    def test_setup_operator(self):
        for number_owners in range(1, 4):
            safe_operator = self.setup_operator(number_owners=number_owners)
            self.assertEqual(len(safe_operator.accounts), number_owners)
            safe = Safe(safe_operator.address, self.ethereum_client)
            self.assertEqual(len(safe.retrieve_owners()), number_owners)

    @mock.patch(
        "safe_eth.safe.Safe.contract", new_callable=mock.PropertyMock, return_value=None
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

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        return_value=Dongle(),
    )
    @mock.patch("safe_cli.operators.hw_wallets.ledger_wallet.get_account_by_path")
    def test_load_ledger_cli_owner(
        self, mock_get_account_by_path: MagicMock, mock_init_dongle: MagicMock
    ):
        owner_address = Account.create().address
        safe_address = self.deploy_test_safe(owners=[owner_address]).address
        safe_operator = SafeOperator(safe_address, self.ethereum_node_url)
        safe_operator.hw_wallet_manager.get_accounts = MagicMock(return_value=[])
        safe_operator.load_ledger_cli_owners()
        self.assertEqual(len(safe_operator.hw_wallet_manager.wallets), 0)
        random_address = Account.create().address
        other_random_address = Account.create().address
        safe_operator.hw_wallet_manager.get_accounts.return_value = [
            (random_address, "44'/60'/0'/0/0"),
            (other_random_address, "44'/60'/0'/0/1"),
        ]

        mock_get_account_by_path.return_value = LedgerAccount(
            "44'/60'/0'/0/0", random_address
        )
        safe_operator.load_ledger_cli_owners()
        self.assertEqual(len(safe_operator.hw_wallet_manager.wallets), 1)
        # Wallet without funds shouldn't be added as sender
        self.assertIsNone(safe_operator.hw_wallet_manager.sender)
        self.assertEqual(
            safe_operator.hw_wallet_manager.wallets.pop().address, random_address
        )

        # Only accept ethereum derivation paths
        with self.assertRaises(HardwareWalletException):
            safe_operator.load_ledger_cli_owners(derivation_path="44'/137'/0'/0/1")
        mock_get_account_by_path.return_value = LedgerAccount(
            "44'/60'/0'/0/0", owner_address
        )
        safe_operator.load_ledger_cli_owners(derivation_path="44'/60'/0'/0/0")
        self.assertEqual(len(safe_operator.hw_wallet_manager.wallets), 1)
        self.assertEqual(
            safe_operator.hw_wallet_manager.wallets.pop().address, owner_address
        )

        # Should be loaded as sender
        ledger_random_address = Account.create().address
        # Send funds to define it as sender
        self.send_ether(ledger_random_address, Wei(1000))
        mock_get_account_by_path.return_value = LedgerAccount(
            "44'/60'/0'/0/1", ledger_random_address
        )
        safe_operator.load_ledger_cli_owners(derivation_path="44'/60'/0'/0/1")
        self.assertEqual(len(safe_operator.hw_wallet_manager.wallets), 1)
        self.assertEqual(
            safe_operator.hw_wallet_manager.sender.address, ledger_random_address
        )

        # test unload ledger owner
        safe_operator.unload_cli_owners([ledger_random_address])
        self.assertEqual(len(safe_operator.hw_wallet_manager.wallets), 0)
        self.assertIsNone(safe_operator.hw_wallet_manager.sender)

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

    @mock.patch("safe_cli.safe_addresses._get_valid_contract")
    def test_sign_message(self, mock_sign_message_lib_address):
        safe_address = self.deploy_test_safe(
            owners=[self.ethereum_test_account.address]
        ).address
        safe_operator = SafeOperator(safe_address, self.ethereum_node_url)
        mock_sign_message_lib_address.return_value = self.deploy_sign_message_lib()
        message = "Safe2024"
        safe_operator.accounts.add(self.ethereum_test_account)
        safe_operator.default_sender = self.ethereum_test_account
        message_hash = safe_operator.safe.get_message_hash(bytes(message, "utf-8"))
        with mock.patch("builtins.input", return_value=message):
            safe_operator.sign_message()

        self.assertTrue(safe_operator.safe.retrieve_is_message_signed(message_hash))
        eip712_path = "tests/mocks/mock_eip712.json"
        message = json.load(open(eip712_path, "r"))
        message_hash = safe_operator.safe.get_message_hash(
            b"".join(eip712_encode(message))
        )
        self.assertFalse(safe_operator.safe.retrieve_is_message_signed(message_hash))
        safe_operator.sign_message(eip712_message_path=eip712_path)
        self.assertTrue(safe_operator.safe.retrieve_is_message_signed(message_hash))

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
        safe_operator = self.setup_operator(version="1.3.0")
        with self.assertRaises(SafeVersionNotSupportedException):
            safe_operator.change_master_copy(self.safe_contract_V1_4_1.address)

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

    @mock.patch.object(
        SafeOperator, "last_default_fallback_handler_address", new_callable=PropertyMock
    )
    @mock.patch.object(
        SafeOperator, "last_safe_contract_address", new_callable=PropertyMock
    )
    def test_update_version(
        self,
        last_safe_contract_address_mock: PropertyMock,
        last_default_fallback_handler_address: PropertyMock,
    ):
        last_safe_contract_address_mock.return_value = self.safe_contract_V1_4_1.address
        last_default_fallback_handler_address.return_value = (
            self.compatibility_fallback_handler.address
        )

        safe_operator_v130 = self.setup_operator(version="1.3.0")
        with self.assertRaises(SafeVersionNotSupportedException):
            safe_operator_v130.update_version()

        safe_operator_v111 = self.setup_operator(version="1.1.1")
        with mock.patch.object(
            MultiSend,
            "MULTISEND_CALL_ONLY_ADDRESSES",
            [self.multi_send_contract.address],
        ):
            safe_operator_v111.update_version()

        self.assertEqual(
            safe_operator_v111.safe.retrieve_master_copy_address(),
            last_safe_contract_address_mock.return_value,
        )
        self.assertEqual(
            safe_operator_v111.safe.retrieve_fallback_handler(),
            last_default_fallback_handler_address.return_value,
        )

    def test_update_to_l2_v111(self):
        migration_contract_address = self._deploy_l2_migration_contract()
        safe_operator_v111 = self.setup_operator(version="1.1.1")

        with mock.patch.dict(
            "safe_cli.operators.safe_operator.safe_deployments",
            {
                "1.3.0": {
                    "GnosisSafeL2": {"1337": [self.safe_contract_V1_3_0.address]},
                    "CompatibilityFallbackHandler": {
                        "1337": [self.compatibility_fallback_handler.address]
                    },
                }
            },
        ):
            self.assertEqual(safe_operator_v111.safe.retrieve_version(), "1.1.1")
            safe_operator_v111.update_version_to_l2(migration_contract_address)
            self.assertEqual(
                safe_operator_v111.safe.retrieve_master_copy_address(),
                self.safe_contract_V1_3_0.address,
            )
            self.assertEqual(
                safe_operator_v111.safe.retrieve_fallback_handler(),
                self.compatibility_fallback_handler.address,
            )

    def test_update_to_l2_v130(self):
        migration_contract_address = self._deploy_l2_migration_contract()
        safe_operator_v130 = self.setup_operator(version="1.3.0")

        # For testing v1.3.0 non L2 to L2 update we need 1.3.0 deployed in a different address
        # L2 Migration Contract only checks version but cannot tell apart L2 from not L2
        tx_hash = self.safe_contract_V1_3_0.constructor().transact(
            {"from": self.ethereum_test_account.address}
        )
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        safe_contract_l2_130_address = tx_receipt["contractAddress"]
        with mock.patch.dict(
            "safe_cli.operators.safe_operator.safe_deployments",
            {
                "1.3.0": {
                    "GnosisSafeL2": {"1337": [safe_contract_l2_130_address]},
                }
            },
        ):
            self.assertEqual(safe_operator_v130.safe.retrieve_version(), "1.3.0")
            self.assertEqual(
                safe_operator_v130.safe.retrieve_master_copy_address(),
                self.safe_contract_V1_3_0.address,
            )
            previous_fallback_handler = (
                safe_operator_v130.safe.retrieve_fallback_handler()
            )
            safe_operator_v130.update_version_to_l2(migration_contract_address)
            self.assertEqual(
                safe_operator_v130.safe.retrieve_master_copy_address(),
                safe_contract_l2_130_address,
            )
            self.assertEqual(
                safe_operator_v130.safe.retrieve_fallback_handler(),
                previous_fallback_handler,
            )

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
