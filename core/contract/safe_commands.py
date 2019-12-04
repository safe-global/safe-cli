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
from hexbytes import HexBytes

# remark: Temporal Owner List, Testing
NULL_ADDRESS = '0x' + '0' * 40
STRING_DASHES = '----------' * 12

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

owners_list = [local_account4, local_account5, local_account6, local_account7, local_account8]


class ConsoleSafeCommands:
    """ Console Safe Commands

    """
    def __init__(self, safe_address, logger, account_artifacts, network_agent):
        self.logger = logger
        self.ethereum_client = network_agent.ethereum_client
        # This should passed from the engine to the controller then to the safe command
        self.safe_operator = Safe(safe_address, self.ethereum_client)
        # This instance should be resolved via blueprint
        self.safe_instance = self._setup_safe_resolver(safe_address)
        # Default gas prices
        self.safe_tx_gas = 300000
        self.base_gas = 200000
        self.gas_price = 0
        # Default empty values
        self.value = 0

        # self.safe_operator.default_owner_address_list almacena los valores del getOwners()
        self.default_owner_address_list = []
        # local accounts from loaded owners via loadOwner --private_key=
        self.local_owner_account_list = []

        self.sender_private_key = None
        self.sender_address = None

        # Main Artifacts for the module
        self.network_agent = network_agent
        self.account_artifacts = account_artifacts

        # Trigger information on class init
        self.command_safe_information()

    # review: search for a blueprint of the version in the functions inputs, removeOwners from 1.0.0 to 1.1.0
    #  recieves diferent data, make a call function and confirm it??
    def _setup_safe_resolver(self, safe_address):
        """

        :param safe_address:
        :return:
        """
        aux_safe_operator = Safe(safe_address, self.ethereum_client)
        safe_version = str(aux_safe_operator.retrieve_version())
        if safe_version == '1.1.0':
            return aux_safe_operator.get_contract()
        elif safe_version == '1.0.0':
            return get_safe_V1_0_0_contract(self.ethereum_client.w3, safe_address)
        else:
            return get_safe_V0_0_1_contract(self.ethereum_client.w3, safe_address)

    def setup_sender(self):
        """ Setup Sender
        This functions will find the best fit owner to be the sender of the transactions, automatically set
        the defaultOwner & defaultOwnerList console variables
        :return:
        """
        stored_ether = []
        self.logger.debug0('Setup Best Fitted Owner As DefaultOwner(Sender) Based On Ether')
        self.logger.debug0(STRING_DASHES)
        for index, owner in enumerate(self.local_owner_account_list):
            account_ether = self.ethereum_client.w3.eth.getBalance(owner.address)
            stored_ether.append(account_ether)
            new_account_data = {
                'network': self.network_agent.network,
                'balance': self.ethereum_client.w3.eth.getBalance(owner.address),
                'address': owner.address, 'private_key': HexBytes(owner.privateKey).hex(),
                'instance': owner
            }
            self.logger.debug0(new_account_data)
            self.logger.debug0(STRING_DASHES)

        self.logger.debug0(STRING_DASHES)
        self.logger.debug0(stored_ether)
        owner_based_on_index = stored_ether.index(max(stored_ether))
        self.logger.debug0(str(owner_based_on_index) + ' | ' + str(stored_ether[stored_ether.index(max(stored_ether))]))
        self.logger.debug0(STRING_DASHES)
        # remark:
        self.sender_address = self.local_owner_account_list[owner_based_on_index].address
        self.sender_private_key = HexBytes(self.local_owner_account_list[owner_based_on_index].privateKey).hex()
        self.logger.info('| Default Sender set to Owner with Address: {0} | '.format(self.sender_address))

    def safe_tx_multi_sign(self, safe_tx, signers_list):
        """ Safe Tx Multi Sign
        This function will perform the sign for every member in the signer_list to the current safe_tx
        :param safe_tx:
        :param signers_list:
        :return:
        """
        try:
            # ordered_signers = sorted(signers_list, key=lambda signer: signer.address.lower())
            for signer in signers_list:
                safe_tx.sign(signer.privateKey)
                self.logger.debug0('| Owner Address: {0} | '.format(signer.address))
                self.logger.debug0('| Sign with Private Key: {0} | '.format(signer.privateKey))
                self.logger.debug0(STRING_DASHES)

            # if self.safe_operator.retrieve_is_message_signed(safe_tx.safe_tx_hash):
            #     print(safe_tx.safe_tx_hash, '\n', 'Message has been successfully \'Signed\' by the Owners')
            return safe_tx
        except Exception as err:
            self.logger.error('Unable to multi_sign_safe_tx(): {0} {1}'.format(type(err), err))

    def safe_tx_multi_approve(self, safe_tx, signers_list):
        """ Safe Tx Multi Approve
        This function will perform an approval for every member in the signer_list to the current safe_tx
        :param safe_tx:
        :param signers_list:
        :return:
        """
        try:
            for signer in signers_list:
                self.safe_instance.functions.approveHash(safe_tx.safe_tx_hash).transact({'from': signer.address})
                self.logger.debug0('| Owner Address: {0} | '.format(signer.address))
                self.logger.debug0('| Approving Tx with Hash: {0} | '.format(safe_tx.safe_tx_hash))
                self.logger.debug0(STRING_DASHES)

                # if self.safe_operator.retrieve_is_hash_approved(signer, safe_tx.safe_tx_hash):
                #     # remark: Check if the message/tx is properly approved by the user
                #     print(safe_tx.safe_tx_hash, '\n',
                #           'Hash has been successfully \'Approved\' by the Owner with Address [ {0} ]'.format(signer.address))
        except Exception as err:
            self.logger.error('Unable to multi_approve_safe_tx(): {0} {1}'.format(type(err), err))

    def perform_transaction(self, payload_data, wei_value=0):
        """ Perform Transaction
        This function will perform the transaction to the safe we have currently triggered via console command
        :param payload_data:
        :param sender:
        :return:
        """
        try:
            if wei_value != 0:
                self.value = wei_value
            # Retrieve Nonce for the transaction
            safe_nonce = self.safe_operator.retrieve_nonce()
            safe_tx = SafeTx(
                self.ethereum_client, self.safe_instance.address, self.safe_instance.address, self.value,
                payload_data, SafeOperation.CALL.value, self.safe_tx_gas, self.base_gas,
                self.gas_price, NULL_ADDRESS, NULL_ADDRESS, safe_nonce=safe_nonce
            )
            # Multi Sign the current transaction
            safe_tx = self.safe_tx_multi_sign(safe_tx, self.local_owner_account_list)
            safe_tx_receipt = None
            # The current tx was well formed
            if safe_tx.call():
                # Execute the current transaction
                safe_tx_hash, _ = safe_tx.execute(self.sender_private_key, self.base_gas + self.safe_tx_gas)
                # Retrieve the receipt
                safe_tx_receipt = self.ethereum_client.get_transaction_receipt(safe_tx_hash, timeout=60)

                self.logger.info('| Safe Tx Receipt: | ')
                self.logger.info(STRING_DASHES)
                self.logger.info('| Retrieving Tx with Hash: {0} | '.format(safe_tx.safe_tx_hash))
                self.logger.info('{0}'.format(safe_tx_receipt))
                return safe_tx_receipt
        except Exception as err:
            self.logger.error('Unable to perform_transaction(): {0} {1}'.format(type(err), err))

    def command_safe_information(self):
        """ Command Safe Information
        This function will retrieve and show any pertinent information regarding the current safe
        :return:
        """
        banner = '| Safe Information |'.center(120, '-')
        self.logger.info(banner)
        self.command_safe_get_owners()
        self.command_safe_get_threshold()
        self.logger.info('| MasterCopyName: {0} | '.format(self.safe_instance.functions.NAME().call()))
        self.logger.info('| MasterCopy: {0} | '.format(self.safe_operator.retrieve_master_copy_address()))
        self.logger.info('| MasterCopyVersion: {0} | '.format(self.safe_operator.retrieve_version()))
        self.logger.info('| Proxy: {0} | '.format(self.safe_operator.address))
        self.logger.info('| FallBack Handler: {0} | '.format('0x'))
        self.command_safe_nonce()

    def command_set_default_sender(self):
        """

        :return:
        """
        self.logger.info('To Be Implemented')

    def command_set_default_owner_list(self):
        """

        :return:
        """
        self.logger.info('To Be Implemented')

    def command_view_default_sender(self):
        """

        :return:
        """
        self.logger.info(STRING_DASHES)
        self.logger.info('| Default Sender is Owner with Address: {0} | '.format(self.sender_address))
        self.logger.info('| Default Sender is Owner with Private Key: {0} | '.format(self.sender_private_key))
        self.logger.info(STRING_DASHES)

    def command_safe_nonce(self):
        """ Command Safe Nonce
        This function will retrieve and show the nonce value of the safe
        :return:
        """
        self.logger.info('| Nonce: {0} | '.format(self.safe_operator.retrieve_nonce()))
        self.logger.debug0(STRING_DASHES)

    def command_safe_code(self):
        """ Command Safe Code
        This function will retrieve and show the code value of the safe
        :return: code of the safe
        """
        self.logger.info('| Code: {0} | '.format(self.safe_operator.retrieve_code()))
        self.logger.debug0(STRING_DASHES)

    def command_safe_version(self):
        """ Command Safe Version
        This function will retrieve and show the VERSION value of the safe
        :return: version of the safe
        """
        self.logger.info('| MasterCopyVersion: {0} | '.format(self.safe_operator.retrieve_version()))
        self.logger.debug0(STRING_DASHES)

    def command_safe_name(self):
        """ Command Safe Name
        This function will retrieve and show the NAME value of the safe
        :return:
        """
        self.logger.info('| MasterCopyName: {0} | '.format(self.safe_instance.functions.NAME().call()))
        self.logger.debug0(STRING_DASHES)

    def command_safe_get_owners(self):
        """ Command Safe Get Owners
        This function will
        :return:
        """
        for owner_index, owner in enumerate(self.safe_instance.functions.getOwners().call()):
            self.logger.info('| Owner {0} with Address: {1} | '.format(owner_index, owner))
        self.logger.debug0(STRING_DASHES)

    def command_safe_get_threshold(self):
        """ Command Safe Get Threshold
        This function will retrieve and show the threshold of the safe
        :return:
        """
        self.logger.info('| Threshold: {0} | '.format(self.safe_instance.functions.getThreshold().call()))
        self.logger.debug0(STRING_DASHES)

    def command_safe_is_owner(self, owner_address):
        """ Command Safe isOwner
        This function will check if any given owner is part of the safe owners
        :param owner_address:
        :return: True if it's a owner, otherwise False
        """
        self.logger.info('| Owner with Address: {0} | isOwner: {1}  | '.format(owner_address, self.safe_operator.retrieve_is_owner(owner_address)))
        self.logger.debug0(STRING_DASHES)

    def command_safe_are_owners(self, owners_list):
        """ Command Safe areOwners
        This function will check if a list of any given owners is part of the safe owners
        :param owners_list:
        :return: True if it's a owner, otherwise False
        """
        self.logger.debug0(STRING_DASHES)
        for owner_address in owners_list:
            self.command_safe_is_owner(owner_address)

    def command_safe_swap_owner(self, previous_owner, owner, new_owner):
        """ Command Safe Swap Owner | Change Owner
        This function will perform the necessary step for properly executing the method swapOwners from the safe
        :param previous_owner:
        :param owner:
        :param new_owner:
        :return:
        """
        # give list of owners and get the previous owner
        try:
            # Default sender data, since the sender is a local account just sender.addres
            sender_data = {'from': str(self.sender_address), 'gas': 200000, 'gasPrice': 0}

            # Generating the function payload data
            # Swap Owner - address previousOwner, address Owner, addres NewAddress
            payload_data = HexBytes(self.safe_instance.functions.swapOwner(str(previous_owner), str(owner), str(new_owner)).buildTransaction(sender_data)['data'])
            self.logger.debug0(' | Sender Data: {0} | '.format(str(sender_data)))
            self.logger.debug0(STRING_DASHES)
            self.logger.debug0(' | Payload Data: {0} | '.format(str(payload_data)))
            self.logger.debug0(STRING_DASHES)

            # Perform the transaction
            self.perform_transaction(payload_data)

            # Preview the current status of the safe since the transaction
            self.command_safe_get_owners()
        except Exception as err:
            self.logger.error('Unable to command_safe_swap_owner(): {0} {1}'.format(type(err), str(err)))

    def command_safe_change_threshold(self, new_threshold):
        """ Command Safe Change Threshold
        This function will perform the necessary step for properly executing the method changeThreshold from the safe
        :param new_threshold:
        :return:
        """
        try:
            # Default sender data
            sender_data = {'from': str(self.sender_address), 'gas': 200000, 'gasPrice': 0}

            # Generating the function payload data
            payload_data = self.safe_instance.functions.changeThreshold(new_threshold).buildTransaction(sender_data)['data']
            self.logger.debug0(' | Sender Data: {0} | '.format(sender_data))
            self.logger.debug0(STRING_DASHES)
            self.logger.debug0(' | Payload Data: {0} | '.format(payload_data))
            self.logger.debug0(STRING_DASHES)

            # Perform the transaction
            self.perform_transaction(payload_data)

            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
        except Exception as err:
            self.logger.error('Unable to command_safe_change_threshold(): {0} {1}'.format(type(err), err))

    def command_safe_add_owner_threshold(self, new_owner_address, new_threshold=None):
        """ Command Safe Change Threshold
        This function will perform the necessary step for properly executing the method addOwnerWithThreshold from the safe
        :param new_owner_address:
        :param new_threshold:
        :return:
        """
        try:
            # note: Sender data can be set using newPayload and then setDefaultSenderPayload
            # Default sender data
            sender_data = {'from': self.sender_address, 'gas': 200000, 'gasPrice': 0}
            # <>
            if new_threshold is None:
                new_threshold = self.safe_operator.retrieve_threshold() + 1

            # Invalidar operacion si el threshold es mayor que el numero de owners presentes en al lista
            # elif (len(self.safe_instance.functions.getOwners().call()) < self.safe_operator.retrieve_threshold()):
            #     self.logger.error('Invalid Threshold Amount')
            #     raise Exception

            # Generating the function payload data
            payload_data = self.safe_instance.functions.addOwnerWithThreshold(new_owner_address, new_threshold).buildTransaction(sender_data)['data']
            self.logger.debug0(' | Sender Data: {0} | '.format(sender_data))
            self.logger.debug0(STRING_DASHES)
            self.logger.debug0(' | Payload Data: {0} | '.format(payload_data))
            self.logger.debug0(STRING_DASHES)

            # Perform the transaction
            self.perform_transaction(payload_data)

            # Preview the current status of the safe since the transaction
            self.logger.debug0(STRING_DASHES)
            self.command_safe_get_threshold()
            self.command_safe_get_owners()
            self.logger.debug0(STRING_DASHES)
        except Exception as err:
            self.logger.error('Unable to command_safe_add_owner_threshold(): {0} {1}'.format(type(err), err))

    def command_safe_remove_owner(self, previous_owner_address, owner_address):
        """ Command Safe Change Threshold
        This function will perform the necessary step for properly executing the method removeOwner from the safe
        :param previous_owner_address:
        :param owner_address:
        :return:
        """
        try:
            # Default sender data
            sender_data = {'from': str(self.sender_address), 'gas': 200000, 'gasPrice': 0}
            new_threshold = self.safe_operator.retrieve_threshold() - 1
            # Generating the function payload data
            self.logger.info(STRING_DASHES)
            self.logger.info('| Sender: {0} | Previous Owner: {1} | Owner to Remove: {2} | Threshold: {3} | '.format(self.sender_address, previous_owner_address, owner_address, new_threshold))
            self.logger.info(STRING_DASHES)
            payload_data = self.safe_instance.functions.removeOwner(previous_owner_address, owner_address, int(new_threshold)).buildTransaction(sender_data)['data']
            self.logger.debug0('| Sender Data: {0} | '.format(sender_data))
            self.logger.debug0(STRING_DASHES)
            self.logger.debug0('| Payload Data: {0} | '.format(payload_data))
            self.logger.debug0(STRING_DASHES)

            # Perform the transaction
            self.perform_transaction(payload_data)

            # Preview the current status of the safe since the transaction
            self.logger.debug0(STRING_DASHES)
            self.command_safe_get_owners()
            self.logger.debug0(STRING_DASHES)
        except Exception as err:
            self.logger.error('Unable to command_safe_remove_owner(): {0} {1}'.format(type(err), err))

    def command_view_owners_balance(self):
        """ Command View Owners Balance
        List the current balance of the
        :return:
        """
        self.logger.debug0(STRING_DASHES)
        for owner_address in self.safe_operator.retrieve_owners():
            self.logger.info(self.ethereum_client.w3.eth.getBalance(owner_address))
        self.logger.debug0(STRING_DASHES)

    # def command_safe_send_ether(self, amount, address_to, approval=False):
    def command_safe_send_ether(self, address_to, wei_value):
        """ Command Safe Send Ether
        This function will perform the necessary step for properly executing the method removeOwner from the safe
        :param wei_value:
        :param address_to:
        :return:
        """
        self.logger.debug0('Previous Balance Values')
        self.logger.debug0(STRING_DASHES)
        self.command_view_owners_balance()
        try:
            # payload_data = dict(
            #     nonce=self.safe_operator.retrieve_nonce(),
            #     gasPrice=0,
            #     gas=self.gas_price,
            #     to=address_to,
            #     value=self.safe_operator.w3.toWei(wei_value, 'wei')
            # )
            payload_data = b''
            self.perform_transaction(payload_data, wei_value)

            # Datos no necesarios pueden ir vacios
            # self.safe_operator.send_multisig_tx(
            #     local_account1, ether_to_transfer, b'', SafeOperation.DELEGATE_CALL.value,
            #     30000, 20000, 1, NULL_ADDRESS, NULL_ADDRESS, b'signatures', local_account1.privateKey
            # )
            self.logger.debug0('Final Balance Values')
            self.logger.debug0(STRING_DASHES)
            self.command_view_owners_balance()

        except Exception as err:
            self.logger.error('Unable to command_safe_send_ether(): {0} {1}'.format(type(err), err))

    def are_enough_signatures_loaded(self):
        """ Are Enough Signatures Loaded
        This funcion eval if the current operation is in disposition to be executed, evaluating the number of threshold
        limiting the execution of operations vs de current lenght of the list of account_local
        :return:
        """
        if self.safe_operator.retrieve_threshold() == self.local_owner_account_list:
            return True
        self.logger.error('Not Enough Signatures Loaded/Stored in local_accounts_list ')
        return False
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