from unittest import mock

from eth_account import Account
from safe_eth.eth import EthereumClient, EthereumNetwork
from safe_eth.safe.tests.safe_test_case import SafeTestCaseMixin
from safe_eth.util.util import to_0x_hex_str

from safe_cli.operators import SafeOperator, SafeOperatorMode, SafeTxServiceOperator


class SafeCliTestCaseMixin(SafeTestCaseMixin):
    def setup_operator(
        self,
        number_owners: int = 1,
        version: str = "1.4.1",
        mode: SafeOperatorMode = SafeOperatorMode.BLOCKCHAIN,
    ) -> SafeOperator:
        assert number_owners >= 1, "Number of owners cannot be less than 1!"
        if version == "1.0.0":
            safe = self.deploy_test_safe_v1_0_0(
                owners=[self.ethereum_test_account.address]
            )
        elif version == "1.1.1":
            safe = self.deploy_test_safe_v1_1_1(
                owners=[self.ethereum_test_account.address]
            )
        elif version == "1.3.0":
            safe = self.deploy_test_safe_v1_3_0(
                owners=[self.ethereum_test_account.address]
            )
        elif version == "1.4.1":
            safe = self.deploy_test_safe_v1_4_1(
                owners=[self.ethereum_test_account.address]
            )
        else:
            raise ValueError(f"{version} not supported")
        if mode == SafeOperatorMode.BLOCKCHAIN:
            safe_operator = SafeOperator(safe.address, self.ethereum_node_url)
        else:
            with mock.patch.object(
                EthereumClient, "get_network", return_value=EthereumNetwork.GOERLI
            ):
                safe_operator = SafeTxServiceOperator(
                    safe.address, self.ethereum_node_url
                )
        safe_operator.load_cli_owners([to_0x_hex_str(self.ethereum_test_account.key)])
        for _ in range(number_owners - 1):
            account = Account.create()
            safe_operator.add_owner(account.address)
            safe_operator.load_cli_owners([to_0x_hex_str(account.key)])
        return safe_operator
