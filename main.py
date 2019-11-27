#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Todo: Maybe Add a listener for the Events done by the contract atleast locally so it can be studied how it behaves
# Todo: Only add to the temporal lexer valid addresses (it has been operated with)
# reference: https://ethereum.stackexchange.com/questions/1374/how-can-i-check-if-an-ethereum-address-is-valid
# reference: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md#implementation

from eth_account import Account
from gnosis.safe.safe_tx import SafeTx
from gnosis.safe.safe_signature import SafeSignature
from gnosis.safe.safe import Safe, SafeOperation
from gnosis.eth.ethereum_client import EthereumClient
from safe_init_scenario_script import gnosis_py_init_scenario

query_is_owner = 'isOwner --address=0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 --query'
execute_swap_owner = 'swapOwner --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002 --from=0x00000000000000000000000000000003 --execute'
query_get_owners = 'getOwners --query'
query_execTransaction_not_enough_args = 'execTransaction --queue --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002'

# is_valid_address = r'^(0x)?[0-9a-f]{40}$'
# is_62_valid_address = r'^(0x)?[0-9a-f]{62}$'
# Currency Utility
# Web3.fromWei(1000000000000000000, 'Gwei')
# Address Utility
# Web3.isAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
# Web3.isChecksumAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')


# remark: transact with arguments
# note: could be autofilled if not provided and set in the console session
NULL_ADDRESS = '0x' + '0'*40

# remark: COMMAND ARGUMENT HERE
command_argument = 'changeThreshold'
argument_list = ''

contract_artifacts = gnosis_py_init_scenario()
ethereum_client = EthereumClient()

private_key_account0 = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
private_key_account1 = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
private_key_account2 = '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
new_account = Account.privateKeyToAccount('0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743')
owners_list = [Account.privateKeyToAccount(private_key_account0), Account.privateKeyToAccount(private_key_account1), Account.privateKeyToAccount(private_key_account2)]
print('[ Accounts ]:', owners_list)

orderred_signers = sorted(owners_list, key=lambda v: v.address.lower())
safe_operator = Safe(contract_artifacts['address'], ethereum_client)
safe_contract = safe_operator.get_contract()

from hexbytes import HexBytes


from gnosis.eth.contracts import (
    get_safe_contract, get_safe_V1_0_0_contract, get_safe_V0_0_1_contract
)

class SafeConsoleMethods:
    def __init__(self, safe_address):
        self.safe_operator = Safe(safe_address, ethereum_client)
        self.safe_instance = self._setup_safe_resolver(safe_address)
        self.safe_tx_gas = 300000
        self.base_gas = 200000
        self.gas_price = 0
        self.value = 0

    def _setup_safe_resolver(self, safe_address):
        safe_operator = Safe(safe_address, ethereum_client)
        safe_version = str(safe_operator.retrieve_version())
        if safe_version == '1.1.0':
            print('version 1.1.0')
            return safe_operator.get_contract()
        elif safe_version == '1.0.0':
            print('version 1.0.0')
            return get_safe_V1_0_0_contract(ethereum_client.w3, safe_address)
        else:
            print('version 0.0.1')
            return get_safe_V0_0_1_contract(ethereum_client.w3, safe_address)


    def multi_sign_safe_tx(self, safe_tx, signers_list):
        try:
            ordered_signers = sorted(signers_list, key=lambda signer: signer.address.lower())
            for account_address in ordered_signers:
                safe_tx.sign(account_address.privateKey)
            return safe_tx
        except Exception as err:
            print(type(err), err)

    def perform_transaction(self, payload_data, nonce, sender_private_key, signers_list, approval=False):
        """

        :param payload_data:
        :param nonce:
        :param sender_private_key:
        :param signers_list:
        :param approval:
        :return:
        """
        safe_tx = SafeTx(ethereum_client, self.safe_instance.address, self.safe_instance.address, self.value,
                         payload_data, SafeOperation.DELEGATE_CALL.value, self.safe_tx_gas, self.base_gas,
                         self.gas_price, NULL_ADDRESS, NULL_ADDRESS, b'', nonce)
        safe_tx = self.multi_sign_safe_tx(safe_tx, owners_list)

        if approval:
            for signer in signers_list:
                self.safe_instance.functions.approveHash(safe_tx.safe_tx_hash).transact({'from': signer.address})

        tx_hash, _ = safe_tx.execute(sender_private_key, self.base_gas + self.safe_tx_gas)
        tx_receipt = ethereum_client.get_transaction_receipt(tx_hash, timeout=60)
        print('Tx Receipt:\n', tx_receipt)
        return tx_receipt

    def _eval_arguments(self, command_argument, argument_list=[]):
        print(safe_operator.retrieve_master_copy_address())
        if command_argument == 'isOwner':
            print(safe_operator.retrieve_is_owner(owners_list[0].address))
            print(safe_operator.retrieve_is_owner(owners_list[1].address))
            print(safe_operator.retrieve_is_owner(owners_list[2].address))

        elif command_argument == 'nonce':
            self.safe_instance.functions.nonce().call()

        elif command_argument == 'code':
            self.safe_instance.functions.nonce().call()

        elif command_argument == 'VERSION':
            self.safe_instance.functions.VERSION().call()

        elif command_argument == 'changeThreshold':
            try:
                nonce = self.safe_instance.functions.nonce().call()
                payload_data = self.safe_instance.functions.changeThreshold(5).buildTransaction({'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
                print('Payload:\n', payload_data)
                self.perform_transaction(payload_data, nonce, owners_list[0].privateKey, owners_list, approval=False)
                print(safe_contract.functions.getThreshold().call())
            except Exception as err:
                print(type(err), err)
        elif command_argument == 'addOwnerWithThreshold':
            nonce = self.safe_instance.functions.nonce().call()
            payload_data = self.safe_instance.functions.addOwnerWithThreshold(new_account.address, 4).buildTransaction({'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
            print('Payload:\n', payload_data)
            self.perform_transaction(payload_data, nonce, owners_list[0].privateKey, owners_list, approval=True)
            print(safe_contract.functions.getOwners().call())
            print(safe_contract.functions.getThreshold().call())

        elif command_argument == 'removeOwner':
            nonce = self.safe_instance.functions.nonce().call()
            payload_data = self.safe_instance.functions.removeOwner(owners_list[0].address, owners_list[1].address, 2).buildTransaction(
                {'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
            print('Payload:\n', payload_data)
            self.perform_transaction(payload_data, nonce, owners_list[0].privateKey, owners_list, approval=True)
            print(safe_contract.functions.getOwners().call())

        elif command_argument == 'swapOwner':
            nonce = self.safe_instance.functions.nonce().call()
            payload_data = self.safe_instance.functions.swapOwner(owners_list[0].address, owners_list[1].address, new_account.address).buildTransaction(
                {'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
            print('Payload:\n', payload_data)
            self.perform_transaction(payload_data, nonce, owners_list[0].privateKey, owners_list, approval=True)
            print(safe_contract.functions.getOwners().call())

        elif command_argument == 'sendToken':
            print('sendToken Operation')

        elif command_argument == 'sendEther':
            print('sendEther Operation')



safe_methods = SafeConsoleMethods(contract_artifacts['address'])
safe_methods._eval_arguments('swapOwner')

# # remark: hardcoded private keys for ganache provider
# private_key_account0 = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
# private_key_account1 = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
# private_key_account2 = '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
# # remark: get Account instances from every private key
# users_to_sign = [Account.privateKeyToAccount(private_key_account0), Account.privateKeyToAccount(private_key_account1),
#                  Account.privateKeyToAccount(private_key_account2)]
# print('[ Accounts ]:', users_to_sign)
# orderred_signers = sorted(users_to_sign, key=lambda v: v.address.lower())
# print(orderred_signers[0].address, 'is Owner?',
#       safe_contract.functions.isOwner(orderred_signers[0].address).call())
# print(orderred_signers[1].address, 'is Owner?',
#       safe_contract.functions.isOwner(orderred_signers[1].address).call())
# print(orderred_signers[2].address, 'is Owner?',
#       safe_contract.functions.isOwner(orderred_signers[2].address).call())
#
# # remark: Data to ve used in the Transaction
# new_account_to_add = Account.create()
# new_account_address = new_account_to_add.address
# base_gas = 400000
# safe_tx_gas = 300000
# gas_price = 0
# nonce = safe_contract.functions.nonce().call()
# current_owners = safe_contract.functions.getOwners().call()
# CALL = 0
#
# # remark: Generate transaction for the addOwnerWithThreshold
# print('\nCurrent Owners of the Safe:\n', current_owners)
# # transaction = safe_contract.functions.addOwnerWithThreshold(new_account_address, 3).buildTransaction({'from': orderred_signers[0].address})
# transaction = safe_contract.functions.changeThreshold(4).buildTransaction({'from': orderred_signers[0].address})
# # transaction.update({'nonce': nonce, 'gasPrice': 1})
# print('Current Transaction: \n', transaction['data'])
#
# # remark: Since we need the Hash for the fucntion to be signed, with the gas data from before we create the
# #  new transaction data: payload of the new transaction
# tx_change_threshold = safe_contract.functions.getTransactionHash(
#     safe_operator.address, 0, transaction['data'], 0, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, nonce
# ).call()
#
# # remark: Sign Transaction Hash
# signature_bytes = b''
# for signers in orderred_signers:
#     tx_signature = signers.signHash(tx_change_threshold)
#     signature_bytes += tx_signature['signature']
# print('[ Output Signature ]: ' + signature_bytes.hex())
#
# try:
#     # remark: Launch the current transaction usign execTransaction
#     change_treshold_hash = safe_contract.functions.execTransaction(
#         safe_operator.address, 0, transaction['data'], 0, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS,
#         signature_bytes
#     ).transact({'from': orderred_signers[0].address, 'gas': safe_tx_gas + base_gas})
#
#     # remark: KEEP WAITING FOR THE TRANSACTION TO BE MINED¡
#     receipt_for_change_threshold = ethereum_client.w3.eth.waitForTransactionReceipt(change_treshold_hash)
#     print('\n', receipt_for_change_threshold)
# except Exception as err:
#     print(err)
# current_threshold = safe_contract.functions.getThreshold().call()
# print('\nThreshold Safe:', current_threshold)