#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Eth Account Package
from eth_account import Account
from core.constants.console_constant import NULL_ADDRESS

# Todo: Finish the multi sign Transaction for the proxy contract.
# note: The contracts will be compiled via subprocess using truffle compile this is maily because the current versions
#  for py-solcx and py-sol reports an error while trying to access the mock contracts in GnosisSafe Project.


def gnosis_test(safe_interface, contract_artifacts, ethereum_client):
    # remark: hardcoded private keys for ganache provider
    private_key_account0 = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    private_key_account1 = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    private_key_account2 = '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
    # remark: get Account instances from every private key
    users_to_sign = [
        Account.privateKeyToAccount(private_key_account0),
        Account.privateKeyToAccount(private_key_account1),
        Account.privateKeyToAccount(private_key_account2)
    ]
    print('[ Accounts ]:', users_to_sign)
    orderred_signers = sorted(users_to_sign, key=lambda v: v.address.lower())
    print(orderred_signers[0].address, 'is Owner?', safe_interface.functions.isOwner(orderred_signers[0].address).call())
    print(orderred_signers[1].address, 'is Owner?', safe_interface.functions.isOwner(orderred_signers[1].address).call())
    print(orderred_signers[2].address, 'is Owner?', safe_interface.functions.isOwner(orderred_signers[2].address).call())

    # remark: Data to ve used in the Transaction
    CALL = 0
    gas_price = 0
    base_gas = 200000
    safe_tx_gas = 300000

    nonce = safe_interface.functions.nonce().call()
    current_owners = safe_interface.functions.getOwners().call()
    proxy_address = contract_artifacts['Proxy']['address']

    # remark: Generate transaction for the addOwnerWithThreshold
    print('\nCurrent Owners of the Safe:\n', current_owners)
    transaction = safe_interface.functions.changeThreshold(3).buildTransaction({'from': proxy_address})
    print('Current Transaction: \n', transaction['data'])

    # remark: Since we need the Hash for the fucntion to be signed, with the gas data from before we create the
    #  new transaction data: payload of the new transaction
    tx_change_threshold = safe_interface.functions.getTransactionHash(
        proxy_address, 0, transaction['data'], CALL, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, nonce
    ).call()

    # remark: Sign Transaction Hash
    signature_bytes = b''
    for signers in orderred_signers:
        tx_signature = signers.signHash(tx_change_threshold)
        signature_bytes += tx_signature['signature']
    print('[ Output Signature ]: ' + signature_bytes.hex())

    try:
        # remark: Launch the current transaction usign execTransaction
        change_treshold_hash = safe_interface.functions.execTransaction(
            proxy_address, 0, transaction['data'], 0, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, signature_bytes
        ).transact({'from': orderred_signers[0].address, 'gas': safe_tx_gas + base_gas})

        # remark: KEEP WAITING FOR THE TRANSACTION TO BE MINED¡
        receipt_for_change_threshold = ethereum_client.w3.eth.waitForTransactionReceipt(change_treshold_hash)
        print('\n', receipt_for_change_threshold)
    except Exception as err:
        print(err)
    current_owners = safe_interface.functions.getThreshold().call()
    print('\nCurrent Owners of the Safe:\n', current_owners)
