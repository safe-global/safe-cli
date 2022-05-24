from eth_account.signers.local import LocalAccount

from gnosis.eth.contracts import get_multi_send_contract
from gnosis.eth.tests.utils import deploy_erc20


def send_tx(w3, tx, account: LocalAccount):
    if "nonce" not in tx:
        tx["nonce"] = w3.eth.get_transaction_count(
            account.address, block_identifier="pending"
        )
    if "gasPrice" not in tx and "maxFeePerGas" not in tx:
        tx["gasPrice"] = w3.eth.gas_price
    if "gas" not in tx:
        tx["gas"] = w3.eth.estimate_gas(tx)
    else:
        tx["gas"] *= 2
    signed_tx = account.sign_transaction(dict(tx))
    tx_hash = w3.eth.send_raw_transaction(bytes(signed_tx.rawTransaction))
    w3.eth.wait_for_transaction_receipt(tx_hash)


def deploy_multisend(w3, account: LocalAccount):
    multisend_contract = get_multi_send_contract(w3)
    tx = multisend_contract.constructor().buildTransaction(
        {
            "nonce": w3.eth.get_transaction_count(
                account.address, block_identifier="pending"
            )
        }
    )
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def fill_transactions_erc20(
    w3, safe_operator, account, num_contracts, num_tokens_to_send
):
    for i in range(num_contracts):
        token_name = "MOI" + str(i)
        erc20_contract = deploy_erc20(
            safe_operator.safe.w3,
            token_name,
            token_name,
            account.address,
            10,
            account=account,
        )
        transaction = erc20_contract.functions.transfer(
            safe_operator.address, 1
        ).buildTransaction({"from": account.address})
        nonce = w3.eth.get_transaction_count(
            account.address, block_identifier="pending"
        )
        for i in range(num_tokens_to_send):
            transaction["nonce"] = nonce
            send_tx(w3, transaction, account)
            nonce += 1
