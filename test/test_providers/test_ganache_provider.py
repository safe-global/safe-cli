#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import pytest
#
#
# def test_deploy_contracts():
#     # with pytest.raises(ZeroDivisionError):
#     return
#
#
# def test_gnosis_setup():
#     return
# print('\n[ Testing Basic Calls ]')
#     print('---------' * 10)
#     print(functional_safe.functions.NAME().call())
#     print(functional_safe.functions.VERSION().call())
#     print(functional_safe.functions.isOwner('0xe982E462b094850F12AF94d21D470e21bE9D0E9C').call())
#     print(functional_safe.functions.isOwner('0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1').call())
#     print(functional_safe.functions.getThreshold().call())
#     print(functional_safe.functions.getOwners().call())
#     print('Done.')
#
#     print('\n[ Basic Transfer Calls Withing Ganache Accounts, Random Account & Proxy Safe ]')
#     print('---------' * 10)
#
#     account = Account.create()
#     random_account_address = account.address
#     random_private_key = account.privateKey
#
#     print('[ Generate Account() ]')
#     print(' (+) Random Address: ', random_account_address)
#     print(' (+) Random Private Key: ', random_private_key)
#     print('Done.\n')
#
#     provider = ganache_provider.get_provider()
#     account2 = provider.eth.accounts[2]
#     account1 = provider.eth.accounts[1]
#
#
#     print('-------' * 10)
#     print('[ Summary ]: From Ganache Account To Random Account Transfer')
#     print(' (+) Balance in Safe Proxy Account: ', provider.eth.getBalance(str(contract_artifacts['Proxy']['address'])))
#     print(' (+) Balance in Random Account: ', provider.eth.getBalance(str(random_account_address)))
#     print(' (+) Balance in Ganache Account: ', provider.eth.getBalance(str(account2)))
#     print('Done.\n')
#
#     # Tx Data
#     tx_data0 = dict(
#         nonce=provider.eth.getTransactionCount(str(account2)),
#         gasPrice=provider.eth.gasPrice,
#         gas=100000,
#         to=str(random_account_address),
#         value=provider.toWei(1.2, 'ether')
#     )
#     signed_txn = provider.eth.account.signTransaction(tx_data0, private_key_account2)
#     tmp_txn_hash = provider.eth.sendRawTransaction(signed_txn.rawTransaction)
#
#     # Wait for the transaction to be mined, and get the transaction receipt
#     receipt_txn_hash = provider.eth.waitForTransactionReceipt(tmp_txn_hash)
#     tx_history.add_tx_to_history(ganache_provider['name'], account2, receipt_txn_hash, tx_data0)
#
#     print('-------' * 10)
#     print('[ Summary ]: From Ganache Account To Random Account Transfer')
#     print(' + Balance in Safe Proxy Account: ', provider.eth.getBalance(str(contract_artifacts['Proxy']['address'])))
#     print(' + Balance in Random Account: ', provider.eth.getBalance(str(random_account_address)))
#     print(' + Balance in Ganache Account: ', provider.eth.getBalance(str(account2)))
#     print('Done.\n')
#
#     # Tx Data
#     tx_data1 = dict(
#         nonce=provider.eth.getTransactionCount(str(random_account_address)),
#         gasPrice=provider.eth.gasPrice,
#         gas=100000,
#         to=str(contract_artifacts['Proxy']['address']),
#         value=provider.toWei(1.1, 'ether')
#     )
#
#     random_acc_signed_txn = provider.eth.account.signTransaction(tx_data1, random_private_key)
#     random_acc_tmp_txn_hash = provider.eth.sendRawTransaction(random_acc_signed_txn.rawTransaction)
#
#     # Wait for the transaction to be mined, and get the transaction receipt
#     random_acc_receipt_txn_hash = provider.eth.waitForTransactionReceipt(random_acc_tmp_txn_hash)
#
#     tx_history.add_tx_to_history(ganache_provider['name'], random_account_address, random_acc_receipt_txn_hash, tx_data1)
#     print('-------' * 10)
#     print('[ Summary ]: From Random Account To Proxy Safe Account Transfer')
#     print(' + Balance in Safe Proxy Account: ', provider.eth.getBalance(str(contract_artifacts['Proxy']['address'])))
#     print(' + Balance in Random Account: ', provider.eth.getBalance(str(random_account_address)))
#     print(' + Balance in Ganache Account: ', provider.eth.getBalance(str(account2)))
#     print('Done.\n')
#     print('-------' * 10)
#     print('[ Summary ]: Transaction History')
#     print(tx_history.history)
#     print('Done.\n')
#
#     # note: Send Money to a Newly created account in the network, and lastly beetween safes?
#     # note: Make Tx from the Safe
#     # reference: https://gnosis-safe.readthedocs.io/en/version_0_0_2/services/relay.html
#     # reference: https://ethereum.stackexchange.com/questions/760/how-is-the-address-of-an-ethereum-contract-computed/761#761
#     # note: The proxy contract implements only two functions: The constructor setting the address of the master copy
#     multi_sig_to = Account.create()
#     multi_sig_address = multi_sig_to.address
#     multi_sig_private_key = multi_sig_to.privateKey
#     print('[ Generate Account() ]')
#     print(' (+) 2ºRandom Address: ', multi_sig_address)
#     print(' (+)) 2ºRandom Private Key: ', multi_sig_private_key)
#     print('Done.\n')
#
#     CREATE = 2
#     DELEGATE_CALL = 1
#     CALL = 0
#
#     # VARIABLES IN THE MULTISIGN EXAMPLE
#     address_to = multi_sig_address
#     value = provider.toWei(1, 'ether')
#     data = b''
#     operation = CALL
#     safe_tx_gas = 300
#     base_gas = 10
#     gas_price = 0
#     address_gas_token = NULL_ADDRESS
#     address_refund_receiver = NULL_ADDRESS
#     nonce = functional_safe.functions.nonce().call()
#
#     tx_hash_multi_sign = functional_safe.functions.getTransactionHash(
#         address_to, value, data, operation, safe_tx_gas, base_gas, gas_price, address_gas_token, address_refund_receiver, nonce
#     ).call()
#
#     # very_important_data = [Account.from_key(private_key_account1)]
#     very_important_data = [Account.from_key(private_key_account1), Account.from_key(private_key_account2)]
#     print('Input signers', very_important_data)
#     # generar Account y ordenar por address.
#
#     orderred_signers = sorted(very_important_data, key=lambda v: v.address.lower())
#     print('Ordered Signers', orderred_signers[0].privateKey, orderred_signers[0].address)
#     print('Ordered Signers', orderred_signers[1].privateKey, orderred_signers[1].address)
#
#     signature_bytes = b''
#     for signers in orderred_signers:
#         tx_signature = signers.signHash(tx_hash_multi_sign)
#         signature_bytes += tx_signature['signature']
#     print('[ Output Signature ]: ' + signature_bytes.hex())
#
#     functional_safe.functions.approveHash(tx_hash_multi_sign).transact({'from': account1})
#     functional_safe.functions.approveHash(tx_hash_multi_sign).transact({'from': account2})
#     functional_safe.functions.execTransaction(
#         address_to, value, data, CALL, safe_tx_gas, base_gas, gas_price, address_gas_token, address_refund_receiver, signature_bytes
#     ).transact({'from': account1})
#
#     print('-------' * 10)
#     print('[ Summary ]: From Random Account To Proxy Safe Account Transfer')
#     print(' + Balance in Safe Proxy Account: ', provider.eth.getBalance(str(contract_artifacts['Proxy']['address'])))
#     print(' + Balance in Random Account: ', provider.eth.getBalance(str(address_to)))
#     print('Done.\n')
#
#     # note: Build a payload with buildTrasaction with gas:0, gasPrices:0, ... to call for the AccountManager in the Safe.
#     #  Then Call execTransaction() with addOwner, removeOwner, SwapOnwer, changeThreshold etc etc
#     #  functional_safe.functions.addOwnerWithThreshold().call()
#     #  functional_safe.functions.removeOwner().call()
#     #  functional_safe.functions.swapOwner().call()
#
#     # remark: Transaction Flow :: Change Threshold from 2 to 1
#     #  [ Build Transaction ]
#     # nonce = functional_safe.functions.nonce().call()
#     # transaction = functional_safe.functions.changeThreshold(3).buildTransaction({'from': orderred_signers[0].address})
#     # transaction.update({'gas': base_gas})
#     # transaction.update({'gasPrice': gas_price})
#     # transaction.update({'nonce': nonce})
#     #
#     # print('Current Transaction: \n', transaction)
#     # # Using the Payload from buildTransaction, getTransactionHash
#     # tx_change_threshold = functional_safe.functions.getTransactionHash(
#     #     transaction['to'], transaction['value'], transaction['data'], operation, safe_tx_gas, base_gas, gas_price, address_gas_token, address_refund_receiver, nonce
#     # ).call()
#     #
#     # # Sign Transaction Hash
#     # signature_bytes = b''
#     # for signers in orderred_signers:
#     #     tx_signature = signers.signHash(tx_change_threshold)
#     #     signature_bytes += tx_signature['signature']
#     # print('[ Output Signature ]: ' + signature_bytes.hex())
#     #
#     # print(orderred_signers[0].address, 'is Owner?', functional_safe.functions.isOwner(orderred_signers[0].address).call())
#     # print(orderred_signers[1].address, 'is Owner?', functional_safe.functions.isOwner(orderred_signers[1].address).call())
#     #
#     # # Approve Transaction Hash
#     # functional_safe.functions.approveHash(tx_change_threshold).transact({'from': orderred_signers[0].address})
#     # functional_safe.functions.approveHash(tx_change_threshold).transact({'from': orderred_signers[1].address})
#     # # Launch Transaction Hash
#     # print('Previous Threshold', functional_safe.functions.getThreshold().call())
#     # change_treshold_hash = functional_safe.functions.execTransaction(
#     #     transaction['to'], transaction['value'], transaction['data'], CALL, safe_tx_gas, base_gas, gas_price, address_gas_token, address_refund_receiver, signature_bytes
#     # ).transact({'from': orderred_signers[0].address})
#     # receipt_for_change_threshold = provider.eth.waitForTransactionReceipt(change_treshold_hash)
#     # print(receipt_for_change_threshold)
#     # print('New Threshold', functional_safe.functions.getThreshold().call())