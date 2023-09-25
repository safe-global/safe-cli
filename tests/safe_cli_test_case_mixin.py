from eth_account import Account

from gnosis.safe.tests.safe_test_case import SafeTestCaseMixin

from safe_cli.operators.safe_operator import SafeOperator


class SafeCliTestCaseMixin(SafeTestCaseMixin):
    def setup_operator(self, number_owners: int = 1, version="1.4.1") -> SafeOperator:
        assert number_owners >= 1, "Number of owners cannot be less than 1!"
        if version == "1.1.1":
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
        safe_operator = SafeOperator(safe.address, self.ethereum_node_url)
        safe_operator.load_cli_owners([self.ethereum_test_account.key.hex()])
        for _ in range(number_owners - 1):
            account = Account.create()
            safe_operator.add_owner(account.address)
            safe_operator.load_cli_owners([account.key.hex()])
        return safe_operator
