#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.input.console_input_getter import ConsoleInputGetter
from eth_account import Account
from gnosis.safe.safe_tx import SafeTx
from gnosis.safe.safe import Safe, SafeOperation
from gnosis.eth.ethereum_client import EthereumClient
from gnosis.eth.contracts import (
    get_safe_V1_0_0_contract, get_safe_V0_0_1_contract
)

# remark: Temporal Owner List, Testing
NULL_ADDRESS = '0x' + '0' * 40

local_account0 = Account.privateKeyToAccount('0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
local_account1 = Account.privateKeyToAccount('0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1')
local_account2 = Account.privateKeyToAccount('0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c')
local_account3 = Account.privateKeyToAccount('0x646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913')
local_account4 = Account.privateKeyToAccount('0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743')
local_account5 = Account.privateKeyToAccount('0x395df67f0c2d2d9fe1ad08d1bc8b6627011959b79c53d7dd6a3536a33ab8a4fd')
local_account6 = Account.privateKeyToAccount('0xe485d098507f54e7733a205420dfddbe58db035fa577fc294ebd14db90767a52')
local_account7 = Account.privateKeyToAccount('0xa453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3')
local_account8 = Account.privateKeyToAccount('0x829e924fdf021ba3dbbc4225edfece9aca04b929d6e75613329ca6f1d31c0bb4')
local_account9 = Account.privateKeyToAccount('0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773')
new_account = local_account9

owners_list = [local_account0, local_account1, local_account2]
owners_list = [local_account4, local_account5, local_account6, local_account7, local_account8]

class ConsoleSafeMethods:
    def __init__(self, safe_address, logger):
        self.logger = logger
        # review: Coupling here, this should not be here!
        self.console_getter = ConsoleInputGetter(self.logger)
        self.ethereum_client = EthereumClient()
        self.safe_operator = Safe(safe_address, self.ethereum_client)
        self.safe_instance = self._setup_safe_resolver(safe_address)
        self.safe_tx_gas = 300000
        self.base_gas = 200000
        self.gas_price = 0
        self.value = 0

    # review: use the master copy function to retrieve the true version for the proxy contract
    def _setup_safe_resolver(self, safe_address):
        aux_safe_operator = Safe(safe_address, self.ethereum_client)
        safe_version = str(aux_safe_operator.retrieve_version())
        if safe_version == '1.1.0':
            return aux_safe_operator.get_contract()
        elif safe_version == '1.0.0':
            return get_safe_V1_0_0_contract(self.ethereum_client.w3, safe_address)
        else:
            return get_safe_V0_0_1_contract(self.ethereum_client.w3, safe_address)

    def multi_sign_safe_tx(self, safe_tx, signers_list):
        """ Multi Sign SafeTx Object
        This function will apply the sign for every member in the signer_list to the current SafeTx Object.
        :param safe_tx:
        :param signers_list:
        :return:
        """
        try:
            ordered_signers = sorted(signers_list, key=lambda signer: signer.address.lower())
            for signer in ordered_signers:
                safe_tx.sign(signer.privateKey)

            # remark: Check if the message/tx is properly signed by the user
            if self.safe_operator.retrieve_is_message_signed(safe_tx.safe_tx_hash):
                print(safe_tx.safe_tx_hash, '\n', 'Message has been successfully \'Signed\' by the Owners')
            return safe_tx
        except Exception as err:
            print(type(err), err)

    def perform_transaction(self, sender_private_key, signers_list, payload_data, nonce, approval=False):
        """
        This function will perform the transaction to the safe we have currently load.
        :param payload_data:
        :param nonce:
        :param sender_private_key:
        :param signers_list:
        :param approval:
        :return:
        """
        safe_tx = SafeTx(self.ethereum_client, self.safe_instance.address, self.safe_instance.address, self.value,
                         payload_data, SafeOperation.DELEGATE_CALL.value, self.safe_tx_gas, self.base_gas,
                         self.gas_price, NULL_ADDRESS, NULL_ADDRESS, b'', nonce)
        safe_tx = self.multi_sign_safe_tx(safe_tx, owners_list)

        if approval:
            for signer in signers_list:
                self.safe_instance.functions.approveHash(safe_tx.safe_tx_hash).transact({'from': signer.address})
                if self.safe_operator.retrieve_is_hash_approved(signer, safe_tx.safe_tx_hash):
                    # remark: Check if the message/tx is properly approved by the user
                    print(safe_tx.safe_tx_hash, '\n', 'Hash has been successfully \'Approved\' by the Owner with Address [ {0} ]'.format(signer.address))

        tx_hash, _ = safe_tx.execute(sender_private_key, self.base_gas + self.safe_tx_gas)
        tx_receipt = self.ethereum_client.get_transaction_receipt(tx_hash, timeout=60)
        print('Tx Receipt:\n', tx_receipt)
        return tx_receipt

    def operate_with_safe(self, stream):
        """
        This function will evaluate the arguments been send by the user
        :param command_argument:
        :param argument_list:
        :return:
        """
        desired_parsed_item_list, priority_group, command_argument, argument_list = self.console_getter.get_gnosis_input_command_argument(stream)
        print('operate_with_safe', command_argument)
        if command_argument == 'info':
            print('+' + '---------' * 10 + '+')
            print(' MasterCopy Address:', self.safe_operator.retrieve_master_copy_address())
            print(' Proxy Address:', self.safe_operator.address)
            print(' Safe Nonce:', self.safe_operator.retrieve_nonce())
            print(' Safe Version:', self.safe_operator.retrieve_version())
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'getOwners':
            print('+' + '---------' * 10 + '+')
            print(self.safe_instance.functions.getOwners().call())
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'getThreshold':
            print('+' + '---------' * 10 + '+')
            print(self.safe_instance.functions.getThreshold().call())
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'isOwner':
            print('+' + '---------' * 10 + '+')
            print(self.safe_operator.retrieve_is_owner(owners_list[0].address))
            print(self.safe_operator.retrieve_is_owner(owners_list[1].address))
            print(self.safe_operator.retrieve_is_owner(owners_list[2].address))
            print(self.safe_operator.retrieve_is_owner(owners_list[3].address))
            print(self.safe_operator.retrieve_is_owner(owners_list[4].address))
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'nonce':
            print('+' + '---------' * 10 + '+')
            print(self.safe_operator.retrieve_nonce())
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'code':
            print('+' + '---------' * 10 + '+')
            print(self.safe_operator.retrieve_code())
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'VERSION':
            print('+' + '---------' * 10 + '+')
            print(self.safe_operator.retrieve_version())
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'NAME':
            print('+' + '---------' * 10 + '+')
            print(self.safe_instance.functions.NAME().call())
            print('+' + '---------' * 10 + '+')
        elif command_argument == 'changeThreshold':
            try:
                nonce = self.safe_instance.functions.nonce().call()
                payload_data = self.safe_instance.functions.changeThreshold(5).buildTransaction({'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
                print('Payload:\n', payload_data)
                self.perform_transaction(owners_list[0].privateKey, owners_list, payload_data, nonce, approval=True)
                print(self.safe_instance.functions.getThreshold().call())
            except Exception as err:
                print(type(err), err)

        elif command_argument == 'addOwnerWithThreshold' or command_argument == 'addOwner':
            try:
                nonce = self.safe_instance.functions.nonce().call()
                payload_data = self.safe_instance.functions.addOwnerWithThreshold(new_account.address, 4).buildTransaction({'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
                print('Payload:\n', payload_data)
                self.perform_transaction(owners_list[0].privateKey, owners_list, payload_data, nonce, approval=False)
                print(self.safe_instance.functions.getOwners().call())
                print(self.safe_instance.functions.getThreshold().call())
            except Exception as err:
                print(type(err), err)

        elif command_argument == 'removeOwner':
            try:
                nonce = self.safe_instance.functions.nonce().call()
                payload_data = self.safe_instance.functions.removeOwner(owners_list[0].address, owners_list[1].address).buildTransaction(
                    {'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
                print('Payload:\n', payload_data)
                self.perform_transaction(owners_list[0].privateKey, owners_list, payload_data, nonce, approval=False)
                print(self.safe_instance.functions.getOwners().call())
            except Exception as err:
                print(type(err), err)

        elif command_argument == 'swapOwner' or command_argument == 'changeOwner':
            try:
                nonce = self.safe_instance.functions.nonce().call()
                payload_data = self.safe_instance.functions.swapOwner(owners_list[0].address, owners_list[1].address, new_account.address).buildTransaction(
                    {'from': owners_list[0].address, 'gas': 200000, 'gasPrice': 0})['data']
                print('Payload:\n', payload_data)
                self.perform_transaction(payload_data, nonce, owners_list[0].privateKey, owners_list, approval=True)
                print(self.safe_instance.functions.getOwners().call())
            except Exception as err:
                print(type(err), err)

        elif command_argument == 'sendToken':
            print('sendToken Operation')
            print('Perform transaction')

        elif command_argument == 'sendEther':
            print('sendEther Operation')
            print('Eval --ether=, --miliether= inputs, sum it')
            print('Perform transaction')

        elif command_argument == 'updateSafe':
            print('updateSafe Operation: --address=0x...')
            print('step 1: Check Validity of The Safe Address & Version, Then Ask for Confirmation')
            print('Perform transaction')


# orderred_signers = sorted(owners_list, key=lambda v: v.address.lower())
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