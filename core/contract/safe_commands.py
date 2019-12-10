#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.artifacts.utils.ether_helper import EtherHelper
from core.logger.log_message_formatter import LogMessageFormatter

# Constants
from core.constants.console_constant import NULL_ADDRESS, STRING_DASHES

# Import HexBytes Module
from hexbytes import HexBytes

# Import Gnosis-Py Modules
from gnosis.safe.safe_tx import SafeTx
from gnosis.safe.safe import Safe, SafeOperation
from gnosis.eth.contracts import (
    get_safe_V1_0_0_contract, get_safe_V0_0_1_contract, get_erc20_contract
)
from eth_account import Account
import time
import asyncio
from threading import Thread

class ConsoleSafeCommands:
    """ Console Safe Commands
    This class will perform the command call to the different artifacts and the class methods
    """
    def __init__(self, safe_address, logger, data_artifacts, network_agent):
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
        self.zero_value = 0

        # local accounts from loaded owners via loadOwner --private_key=
        self.local_owner_account_list = []

        self.sender_private_key = None
        self.sender_address = None

        # Main Artifacts for the module
        self.network_agent = network_agent
        self.account_artifacts = data_artifacts.account_artifacts
        self.token_artifacts = data_artifacts.token_artifacts

        # Setup: Log Formatter
        self.log_formatter = LogMessageFormatter(self.logger)
        self.ether_helper = EtherHelper(self.logger, self.ethereum_client)

        # Trigger information on class init
        self.command_safe_information()

    # review: currently not in use
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

        header_data = '-:[ {0} ]:-'.format('Setup Best Fitted Owner As DefaultOwner(Sender) Based On Ether')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
        for index, owner in enumerate(self.local_owner_account_list):
            account_ether = self.ethereum_client.w3.eth.getBalance(owner.address)
            stored_ether.append(account_ether)
            new_account_data = {
                'network': self.network_agent.network,
                'balance': self.ethereum_client.w3.eth.getBalance(owner.address),
                'address': owner.address, 'private_key': HexBytes(owner.privateKey).hex(),
                'instance': owner
            }
            #self.logger.debug0(new_account_data)
        owner_based_on_index = stored_ether.index(max(stored_ether))
        self.sender_address = self.local_owner_account_list[owner_based_on_index].address
        self.sender_private_key = HexBytes(self.local_owner_account_list[owner_based_on_index].privateKey).hex()
        header_data = '-:[ {0} ]:-'.format('Sender')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
        information_data = ' (#) Address: {0}'.format(self.sender_address)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        information_data = ' (#) Balance: {0}'.format(self.ethereum_client.w3.eth.getBalance(self.sender_address))
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info(' ' + STRING_DASHES)

    def safe_tx_multi_sign(self, safe_tx, signers_list):
        """ Safe Tx Multi Sign
        This function will perform the sign for every member in the signer_list to the current safe_tx
        :param safe_tx:
        :param signers_list:
        :return:
        """
        try:
            header_data = '-:[ {0} ]:-'.format('Signatures')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
            if len(signers_list) >= self.safe_operator.retrieve_threshold():
                for signer in signers_list:
                    safe_tx.sign(signer.privateKey)
                    information_data = ' (#) Owner Address: {0}'.format(signer.address)
                    self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
                    information_data = ' (#) Sign with Private Key: {0}'.format(HexBytes(signer.privateKey).hex())
                    self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
                    self.logger.info(' ' + STRING_DASHES)
                return safe_tx
            else:
                self.logger.info('Not Enough Owners are loaded in the console')
                raise Exception
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
            header_data = '-:[ {0} ]:-'.format('Approval')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

            for signer in signers_list:
                information_data = ' (#) Owner Address: {0}'.format(signer.address)
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
                information_data = ' (#) Approving Tx with Hash: {0}'.format(HexBytes(safe_tx.safe_tx_hash).hex())
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
                self.logger.info(' ' + STRING_DASHES)

                # if self.safe_operator.retrieve_is_hash_approved(signer, safe_tx.safe_tx_hash):
                #     # remark: Check if the message/tx is properly approved by the user
                #     print(safe_tx.safe_tx_hash, '\n',
                #           'Hash has been successfully \'Approved\' by the Owner with Address [ {0} ]'.format(signer.address))
        except Exception as err:
            self.logger.error('Unable to multi_approve_safe_tx(): {0} {1}'.format(type(err), err))

    def perform_transaction(self, payload_data, wei_value=None, address_to=None):
        """ Perform Transaction
        This function will perform the transaction to the safe we have currently triggered via console command
        :param payload_data:
        :param sender:
        :return:
        """
        try:
            if wei_value is None:
                wei_value = 0
            if address_to is None:
                address_to = self.safe_instance.address

            # Retrieve Nonce for the transaction
            safe_nonce = self.safe_operator.retrieve_nonce()
            safe_tx = SafeTx(
                self.ethereum_client, self.safe_instance.address, address_to, wei_value,
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
                if wei_value is None:
                    self.log_formatter.tx_receipt_formatter(safe_tx_receipt, detailed_receipt=True)
                else:
                    self.log_formatter.tx_receipt_formatter(safe_tx_receipt, detailed_receipt=True)
                return safe_tx_receipt
        except Exception as err:
            self.logger.error('Unable to perform_transaction(): {0} {1}'.format(type(err), err))

    def command_safe_information(self):
        """ Command Safe Information
        This function will retrieve and show any pertinent information regarding the current safe
        :return:
        """
        self.log_formatter.log_banner_header('Safe Information')
        self.command_safe_get_owners()
        self.command_view_balance()
        self.command_safe_get_threshold()

        self.log_formatter.log_section_left_side('Safe General Information')
        self.command_safe_name(block_style=False)
        self.command_master_copy(block_style=False)
        self.command_safe_version(block_style=False)
        self.command_proxy(block_style=False)
        self.command_fallback_handler(block_style=False)
        self.command_safe_nonce(block_style=False)
        self.logger.info(' ' + STRING_DASHES)

    def command_fallback_handler(self, block_style=True):
        """ Command Fallback Handler
        This function will retrieve and show the fallback handler address value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Fallback Handler')
        information_data = ' (#) Fallback Handler: {0}'.format(NULL_ADDRESS)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_proxy(self, block_style=True):
        """ Command Proxy
        This function will retrieve and show the proxy address value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Proxy')
        information_data = ' (#) ProxyCopy: {0}'.format(self.safe_operator.address)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_master_copy(self, block_style=True):
        """ Command Master Copy
        This function will retrieve and show the master copy address value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe MasterCopy')
        information_data = ' (#) MasterCopy: {0}'.format(self.safe_operator.retrieve_master_copy_address())
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_view_default_sender(self):
        """ Command View Default Sender
        This function will retrieve and show the sender value of the safe
        :param block_style:
        :return:
        """
        self.log_formatter.log_section_left_side('Safe Sender')
        information_data = ' (#) Address: {0}'.format(self.sender_address)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        information_data = ' (#) Private Key: {0}'.format(self.sender_private_key)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info(' ' + STRING_DASHES)

    def command_safe_nonce(self, block_style=True):
        """ Command Safe Nonce
        This function will retrieve and show the nonce value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Nonce')
        information_data = ' (#) Nonce: {0} '.format(self.safe_operator.retrieve_nonce())
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_safe_code(self, block_style=True):
        """ Command Safe Code
        This function will retrieve and show the code value of the safe
        :param block_style:
        :return: code of the safe
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Code')

        information_data = ' (#) Code: {0} '.format(HexBytes(self.safe_operator.retrieve_code()).hex())
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_safe_version(self, block_style=True):
        """ Command Safe Version
        This function will retrieve and show the VERSION value of the safe
        :param block_style:
        :return: version of the safe
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Version')

        information_data = ' (#) MasterCopy Version: {0} '.format(self.safe_operator.retrieve_version())
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_safe_name(self, block_style=True):
        """ Command Safe Name
        This function will retrieve and show the NAME value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Name')

        information_data = ' (#) MasterCopy Name: {0} '.format(self.safe_instance.functions.NAME().call())
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def is_sender(self, address):
        if address == self.sender_address:
            return 'X'
        return ' '

    def command_safe_get_owners(self):
        """ Command Safe Get Owners
        This function will retrieve and show the get owners of the safe
        :return:
        """
        self.log_formatter.log_section_left_side('Safe Owner Data')
        for owner_index, owner in enumerate(self.safe_instance.functions.getOwners().call()):
            information_data = ' (#) Owner {0} | Address: {1} | Sender: [{2}] | Balance: {3} '.format(owner_index, owner, self.is_sender(owner), self.ethereum_client.w3.eth.getBalance(owner))
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info(' ' + STRING_DASHES)

    def command_safe_get_threshold(self, block_style=True):
        """ Command Safe Get Threshold
        This function will retrieve and show the threshold of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Threshold')

        information_data = ' (#) Threshold: {0} '.format(self.safe_instance.functions.getThreshold().call())
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_safe_is_owner(self, owner_address, block_style=True):
        """ Command Safe isOwner
        This function will check if any given owner is part of the safe owners
        :param owner_address:
        :param block_style:
        :return: True if it's a owner, otherwise False
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Owners')

        information_data = ' (#) Owner with Address: {0} | isOwner: {1} '.format(owner_address, self.safe_operator.retrieve_is_owner(owner_address))
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.logger.info(' ' + STRING_DASHES)

    def command_safe_are_owners(self, owners_list):
        """ Command Safe areOwners
        This function will check if a list of any given owners is part of the safe owners
        :param owners_list:
        :return: True if it's a owner, otherwise False
        """
        self.log_formatter.log_section_left_side('Safe Owners List')
        for owner_address in owners_list:
            self.command_safe_is_owner(owner_address, block_style=False)
        self.logger.info(' ' + STRING_DASHES)

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
            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
            self.command_safe_get_owners()
            # Default sender data, since the sender is a local account just sender.addres
            sender_data = {'from': str(self.sender_address), 'gas': 200000, 'gasPrice': 0}

            # Generating the function payload data
            # Swap Owner - address previousOwner, address Owner, addres NewAddress
            payload_data = HexBytes(self.safe_instance.functions.swapOwner(str(previous_owner), str(owner), str(new_owner)).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            self.perform_transaction(payload_data)

            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
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
            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
            # Default sender data
            sender_data = {'from': str(self.sender_address), 'gas': 200000, 'gasPrice': 0}

            # Generating the function payload data
            payload_data = self.safe_instance.functions.changeThreshold(new_threshold).buildTransaction(sender_data)['data']
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

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
            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
            self.command_safe_get_owners()
            # note: (future?¿) Sender data can be set using newPayload and then setDefaultSenderPayload
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
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            self.perform_transaction(payload_data)

            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
            self.command_safe_get_owners()
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
            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
            self.command_safe_get_owners()
            # Default sender data
            sender_data = {'from': str(self.sender_address), 'gas': 200000, 'gasPrice': 0}
            new_threshold = self.safe_operator.retrieve_threshold() - 1
            # Generating the function payload data
            self.logger.info(STRING_DASHES)
            self.logger.info('| Sender: {0} | Previous Owner: {1} | Owner to Remove: {2} | Threshold: {3} | '.format(self.sender_address, previous_owner_address, owner_address, new_threshold))
            self.logger.info(STRING_DASHES)
            payload_data = self.safe_instance.functions.removeOwner(previous_owner_address, owner_address, int(new_threshold)).buildTransaction(sender_data)['data']
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            self.perform_transaction(payload_data)

            # Preview the current status of the safe since the transaction
            self.command_safe_get_threshold()
            self.command_safe_get_owners()
        except Exception as err:
            self.logger.error('Unable to command_safe_remove_owner(): {0} {1}'.format(type(err), err))

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

    def command_send_token_raw(self, address_to, token_contract_address, token_amount, local_account):
        try:
            self.command_view_token_balance()
            self.log_formatter.log_section_left_side('Send Token')
            safe_tx = self.ethereum_client.erc20.send_tokens(address_to, int(token_amount), token_contract_address, local_account.privateKey)

            # Retrieve the tx_receipt
            tx_receipt = self.ethereum_client.get_transaction_receipt(safe_tx, timeout=60)
            self.log_formatter.tx_receipt_formatter(tx_receipt, detailed_receipt=True)
            self.command_view_token_balance()
            return tx_receipt
        except Exception as err:
            self.logger.debug0(err)

    def command_deposit_token_raw(self, token_address_to, token_amount, local_account):
        tx_receipt = self.command_send_token_raw(self.safe_operator.address, token_address_to, token_amount, local_account)
        return tx_receipt

    # Todo: Fix Me!!!
    def command_withdraw_token_raw(self, address_to, token_contract_address, token_amount, local_account):
        self.command_view_token_balance()
        sender_data = {'from': self.safe_operator.address, 'gasPrice': 0}
        erc20 = get_erc20_contract(self.ethereum_client.w3, token_contract_address)
        safe_tx = erc20.functions.transfer(address_to, int(token_amount)).buildTransaction(sender_data)

        print('Tx Data:', safe_tx['data'])
        safe_tx = self.safe_operator.build_multisig_tx(
            token_contract_address, 0, safe_tx['data'], SafeOperation.CALL.value,
            safe_tx['gas'] + 50000,  self.base_gas, self.gas_price,
            NULL_ADDRESS, NULL_ADDRESS, b''
        )

        # Multi Sign the current transaction
        safe_tx = self.safe_tx_multi_sign(safe_tx, self.local_owner_account_list)
        safe_tx_receipt = None
        # The current tx was well formed
        print('valor:' + str(safe_tx.call()))
        if safe_tx.call():
            # Execute the current transaction
            safe_tx_hash, _ = safe_tx.execute(self.sender_private_key, tx_gas=self.base_gas + self.safe_tx_gas)
            # Retrieve the receipt
            safe_tx_receipt = self.ethereum_client.get_transaction_receipt(safe_tx_hash, timeout=60)

            self.log_formatter.tx_receipt_formatter(safe_tx_receipt, detailed_receipt=True)

        self.command_view_token_balance()
        return safe_tx_receipt

    def command_send_ether_raw(self, address_to, wei_amount, local_account):
        """ Send Ether Raw
        This function will send ether to the address_to, wei_amount, private_key
        :param address_to:
        :param wei_amount:
        :param local_account:
        :return:
        """
        try:
            self.command_view_ether_balance()
            signed_tx = self.ethereum_client.w3.eth.account.signTransaction(dict(
                nonce=self.ethereum_client.w3.eth.getTransactionCount(local_account.address),
                gasPrice=self.gas_price,
                gas=2000000,
                to=address_to,
                value=self.ethereum_client.w3.toWei(wei_amount, 'wei')
            ), HexBytes(local_account.privateKey).hex())

            tx_hash = self.ethereum_client.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            # Retrieve the tx_receipt
            tx_receipt = self.ethereum_client.get_transaction_receipt(tx_hash, timeout=60)
            self.log_formatter.tx_receipt_formatter(tx_receipt, detailed_receipt=True)
            self.command_view_ether_balance()
            return tx_receipt
        except Exception as err:
            self.logger.debug0(err)

    def command_deposit_ether_raw(self, wei_amount, local_account):
        """ Send Ether To Safe
        This function will send ether to the address_to, wei_amount, private_key
        :param wei_amount:
        :param local_account:
        :return:
        """
        tx_receipt = self.command_send_ether_raw(self.safe_operator.address, wei_amount, local_account)
        return tx_receipt

    def command_withdraw_ether_raw(self, wei_amount, address_to):
        """ Send Ether To Safe
        This function will send ether to the address_to, wei_amount, private_key
        :param wei_amount:
        :param address_to:
        :return:
        """
        self.command_view_ether_balance()
        safe_tx = self.safe_operator.build_multisig_tx(
            address_to, wei_amount, b'', SafeOperation.CALL.value, self.safe_tx_gas, self.base_gas, self.gas_price, NULL_ADDRESS, NULL_ADDRESS, b'')
        # safe_tx signatures
        # Multi Sign the current transaction
        safe_tx = self.safe_tx_multi_sign(safe_tx, self.local_owner_account_list)
        safe_tx_receipt = None
        # The current tx was well formed
        if safe_tx.call():
            # Execute the current transaction
            safe_tx_hash, _ = safe_tx.execute(self.sender_private_key, self.base_gas + self.safe_tx_gas)
            # Retrieve the receipt
            safe_tx_receipt = self.ethereum_client.get_transaction_receipt(safe_tx_hash, timeout=60)

            self.log_formatter.tx_receipt_formatter(safe_tx_receipt, detailed_receipt=True)
        self.command_view_ether_balance()
        return safe_tx_receipt

    def command_view_balance(self):
        """ Command View Total Balance of the safe Ether + Tokens(Only if tokens are known via pre-loading)
        This function
        """
        self.command_view_ether_balance()
        self.command_view_token_balance()

    def command_view_ether_balance(self):
        """ Command View Ether Balance
        This function
        """
        self.log_formatter.log_section_left_side('Safe Ether Balance')
        ether_amount = []
        for owner_index, owner in enumerate(self.safe_instance.functions.getOwners().call()):
            ether_amount.append(self.ethereum_client.w3.eth.getBalance(owner))

        wei_amount = self.ether_helper.unify_ether_badge_amounts('--wei', ether_amount)
        human_readable_ether = self.ether_helper.get_proper_ether_amount(wei_amount)
        information_data = ' (#) Total Owners Funds: {0} {1} '.format(human_readable_ether[1], human_readable_ether[0])
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        safe_ether_amount = self.ethereum_client.w3.eth.getBalance(self.safe_instance.address)
        safe_wei_amount = self.ether_helper.unify_ether_badge_amounts('--wei', [safe_ether_amount])
        safe_human_readable_ether = self.ether_helper.get_proper_ether_amount(safe_wei_amount)
        information_data = ' (#) Total Safe Funds: {0} {1} '.format(safe_human_readable_ether[1], safe_human_readable_ether[0])
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info(' ' + STRING_DASHES)

    def command_view_token_balance(self):
        """ Command View Token Balance
        This function
        """
        self.log_formatter.log_section_left_side('Safe Token Balance')
        token_address = []
        token_symbol = []
        for token_item in self.token_artifacts.token_data:
            current_token_address = self.token_artifacts.token_data[token_item]['address']
            # self.logger.info(current_token_address)
            # self.logger.info(self.token_artifacts.token_data[token_item])
            token_symbol.append(token_item)
            token_address.append(current_token_address)

        balance_data = self.ethereum_client.erc20.get_balances(self.safe_operator.address, token_address)
        current_name_to_show = ''
        for index, item in enumerate(balance_data):
            if item['token_address'] is not None:
                for token_item in self.token_artifacts.token_data:
                    current_token_address = self.token_artifacts.token_data[token_item]['address']
                    if current_token_address == item['token_address']:
                        current_name_to_show = token_item
                information_data = ' (#) Total Safe {0} ({1}) Funds: {2} Token'.format(current_name_to_show, item['token_address'], item['balance'])
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info(' ' + STRING_DASHES)
        return
