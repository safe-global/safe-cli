import unittest

from eth_account import Account

from gnosis.eth import EthereumClient
from gnosis.eth.tests.utils import just_test_if_mainnet_node

from safe_cli.safe_addresses import (
    _get_valid_contract,
    get_default_fallback_handler_address,
    get_last_multisend_address,
    get_last_multisend_call_only_address,
    get_proxy_factory_address,
    get_safe_contract_address,
    get_safe_l2_contract_address,
)

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeAddresses(SafeCliTestCaseMixin, unittest.TestCase):
    def test_get_valid_contract(self):
        addresses = [
            Account.create().address,
            Account.create().address,
            self.safe_contract_V1_4_1.address,
            Account.create().address,
        ]
        expected_address = self.safe_contract_V1_4_1.address
        self.assertEqual(
            _get_valid_contract(self.ethereum_client, addresses), expected_address
        )

        with self.assertRaisesRegex(
            ValueError,
            f"Network {self.ethereum_client.get_network().name} is not supported",
        ):
            _get_valid_contract(self.ethereum_client, addresses[:1])

    def test_get_addresses(self):
        mainnet_node = just_test_if_mainnet_node()
        ethereum_client = EthereumClient(mainnet_node)

        self.assertEqual(
            get_safe_contract_address(ethereum_client),
            "0x41675C099F32341bf84BFc5382aF534df5C7461a",
        )
        self.assertEqual(
            get_safe_l2_contract_address(ethereum_client),
            "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762",
        )
        self.assertEqual(
            get_default_fallback_handler_address(ethereum_client),
            "0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99",
        )
        self.assertEqual(
            get_proxy_factory_address(ethereum_client),
            "0x4e1DCf7AD4e460CfD30791CCC4F9c8a4f820ec67",
        )
        self.assertEqual(
            get_last_multisend_address(ethereum_client),
            "0x38869bf66a61cF6bDB996A6aE40D5853Fd43B526",
        )
        self.assertEqual(
            get_last_multisend_call_only_address(ethereum_client),
            "0x40A2aCCbd92BCA938b02010E17A5b8929b49130D",
        )


if __name__ == "__main__":
    unittest.main()
