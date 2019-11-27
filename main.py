#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Todo: Maybe Add a listener for the Events done by the contract atleast locally so it can be studied how it behaves
# Todo: Only add to the temporal lexer valid addresses (it has been operated with)

# validator = Validator.from_callable(
#     is_valid_address, error_message='Not a valid address (Does not contain an 0x).', move_cursor_to_end=True
# )

query_is_owner = 'isOwner --address=0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 --query'
execute_swap_owner = 'swapOwner --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002 --from=0x00000000000000000000000000000003 --execute'
query_get_owners = 'getOwners --query'
query_execTransaction_not_enough_args = 'execTransaction --queue --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002'

# is_valid_address = r'^(0x)?[0-9a-f]{40}$'
# is_62_valid_address = r'^(0x)?[0-9a-f]{62}$'

# def print_kwargs(**kwargs):
#     new_values = ''
#     for key, value in kwargs.items():
#         if key.strip('_') in ['from', 'gas']: # and validated(key, value):
#             new_values += '\'{0}\':{1},'.format(key.strip('_'), value)
#             print(new_values)
#     return new_values
# aux = print_kwargs(_from="Shark", gas=4.5)
# data_to_print = 'data_to_be_printed.transact{%s}' % (aux[:-1])

# reference: https://ethereum.stackexchange.com/questions/1374/how-can-i-check-if-an-ethereum-address-is-valid
# reference: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md#implementation

# Currency Utility
# Gather all the --Gwei, --Kwei etc etc sum up them and give the ''
# if execute:
#     Web3.fromWei(1000000000000000000, 'Gwei')
# #Web3.toWei()
# #Web3.fromWei()

# # Address Utility
# Web3.isAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
# Web3.isChecksumAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')

# remark: transact with arguments
# note: could be autofilled if not provided and set in the console session

from eth_account import Account
from gnosis.safe.safe_tx import SafeTx
from gnosis.safe.safe_signature import SafeSignature
from gnosis.safe.safe import Safe, SafeOperation
from gnosis.eth.ethereum_client import EthereumClient
from safe_init_scenario_script import gnosis_py_init_scenario

contract_artifacts = gnosis_py_init_scenario()
NULL_ADDRESS = '0x' + '0'*40
command_argument = 'changeOwner'
argument_list = ''
ethereum_client = EthereumClient()

private_key_account0 = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
private_key_account1 = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
private_key_account2 = '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
owners_list = [Account.privateKeyToAccount(private_key_account0), Account.privateKeyToAccount(private_key_account1), Account.privateKeyToAccount(private_key_account2)]
print('[ Accounts ]:', owners_list)

orderred_signers = sorted(owners_list, key=lambda v: v.address.lower())
safe_operator = Safe(contract_artifacts['address'], ethereum_client)
functional_safe = contract_artifacts['instance']
safe_contract = safe_operator.get_contract()
from hexbytes import HexBytes


if command_argument == 'isOwner':
    # safe_operator.retrieve_is_owner()
    print()
elif command_argument == 'nonce':
    safe_operator.retrieve_nonce()
elif command_argument == 'code':
    safe_operator.retrieve_code()
elif command_argument == 'VERSION':
    safe_operator.retrieve_version()
elif command_argument == 'changeOwner':
    # SafeSignature(signature, safe_tx_hash)
    nonce = safe_operator.retrieve_nonce()
    payload_data = HexBytes(safe_contract.functions.changeThreshold(4).buildTransaction({'from': owners_list[0].address, 'gasPrice': 0, 'gas': 200000})['data'])
    safe_tx_gas = 300000
    base_gas = 200000
    gas_price = 0
    to = ''
    value = 0
    safe_tx = SafeTx(ethereum_client, safe_operator.address, safe_operator.address, value, payload_data, SafeOperation.DELEGATE_CALL.value, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, safe_nonce=nonce)
    safe_tx.sign(private_key_account0)
    safe_tx.sign(private_key_account1)
    safe_tx.sign(private_key_account2)
    tx_hash, _ = safe_tx.execute(tx_sender_private_key=private_key_account0)
    receipt = ethereum_client.get_transaction_receipt(tx_hash, timeout=60)
    print('Tx Receipt:\n', receipt)
    current_owners = safe_contract.functions.getThreshold().call()
    print('\nCurrent Owners of the Safe:\n', current_owners)

    # tx_change_threshold = functional_safe.functions.getTransactionHash(
    #     transaction['to'], 0, transaction['data'], 0, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, nonce
    # ).call()

    # SafeSignature()
    # signature_bytes = b''
    # for signers in orderred_signers:
    #     tx_signature = signers.signHash(tx_change_threshold)
    #     signature_bytes += tx_signature['signature']
    # print('[ Output Signature ]: ' + signature_bytes.hex())

    # try:
    #     change_treshold_hash = functional_safe.functions.execTransaction(
    #         transaction['to'], 0, transaction['data'], 0, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, signature_bytes
    #     ).transact({'from': orderred_signers[0].address, 'gas': safe_tx_gas + base_gas})
    #     receipt_for_change_threshold = ethereum_client.get_transaction_receipt(change_treshold_hash)
    #     print('Tx Receipt:\n', receipt_for_change_threshold)
    # except Exception as err:
    #     print(err)


    # safe_operator.retrieve_is_hash_approved()
    # to = transaction['to']
    # value = transaction['value']
    # data = transaction['data']
    # operation = SafeOperation.CALL.value
    # safe_tx_gas = 300000
    # base_gas = 200000
    # gas_price = transaction['gasPrice']
    # gas_token = NULL_ADDRESS
    # refund_reciever = NULL_ADDRESS
    # signatures = b''
    # sender_private_key = b''
    # tx_gas = transaction['gas']
    # tx_gas_price = transaction['gasPrice']
    # safe_operator.send_multisig_tx(to, value, data, operation, safe_tx_gas, base_gas, gas_price, gas_token, refund_reciever, signatures, tx_gas, tx_gas_price)