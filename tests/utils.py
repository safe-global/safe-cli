from eth_account.signers.local import LocalAccount
from safe_eth.eth.tests.utils import deploy_erc20, send_tx

from safe_cli.operators import SafeOperator


# Deploy ERC20 tokens and send it to Safe account
def generate_transfers_erc20(
    w3,
    safe_operator: SafeOperator,
    account: LocalAccount,
    num_contracts: int = 3,
    num_tokens_to_send: int = 3,
):

    for i in range(num_contracts):
        token_name = "MOI{i}"
        # Deploy ERC20
        erc20_contract = deploy_erc20(
            safe_operator.safe.w3,
            account,
            token_name,
            token_name,
            account.address,
            10,
        )
        # Create a transaction of 1 token ERC20
        transaction = erc20_contract.functions.transfer(
            safe_operator.address, 1
        ).build_transaction({"from": account.address})
        nonce = w3.eth.get_transaction_count(
            account.address, block_identifier="pending"
        )
        # Execute one transfer per each token to send
        for _ in range(num_tokens_to_send):
            transaction["nonce"] = nonce
            send_tx(w3, transaction, account)
            nonce += 1
