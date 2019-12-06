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
    get_safe_V1_0_0_contract, get_safe_V0_0_1_contract
)


class ConsoleSafeCommands:
    """ Console Safe Commands
    This class will perform the command call to the different artifacts and the class methods
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

        # Setup: Log Formatter
        self.log_formatter = LogMessageFormatter(self.logger)
        self.ether_helper = EtherHelper(self.logger, self.ethereum_client)

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

            for signer in signers_list:
                safe_tx.sign(signer.privateKey)
                information_data = ' (#) Owner Address: {0}'.format(signer.address)
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
                information_data = ' (#) Sign with Private Key: {0}'.format(HexBytes(signer.privateKey).hex())
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
                self.logger.info(' ' + STRING_DASHES)

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
                self.log_formatter.tx_receipt_formatter(safe_tx_receipt)
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
        self.command_safe_get_threshold()

        header_data = '-:[ {0} ]:-'.format('Safe General Information')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
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
            header_data = '-:[ {0} ]:-'.format('Safe Fallback Handler')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
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
            header_data = '-:[ {0} ]:-'.format('Safe Proxy')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
        information_data = ' (#) Proxy: {0}'.format(self.safe_operator.address)
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
            header_data = '-:[ {0} ]:-'.format('Safe MasterCopy')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
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
        header_data = '-:[ {0} ]:-'.format('Safe Sender')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
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
            header_data = '-:[ {0} ]:-'.format('Safe Nonce')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

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
            header_data = '-:[ {0} ]:-'.format('Safe Code')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

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
            header_data = '-:[ {0} ]:-'.format('Safe Version')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

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
            header_data = '-:[ {0} ]:-'.format('Safe Name')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

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
        header_data = '-:[ {0} ]:-'.format('Safe Owner Data')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
        ether_amount = []
        for owner_index, owner in enumerate(self.safe_instance.functions.getOwners().call()):
            ether_amount.append(self.ethereum_client.w3.eth.getBalance(owner))
            information_data = ' (#) Owner {0} | Address: {1} | Sender: [{2}] | Balance: {3} '.format(owner_index, owner, self.is_sender(owner), self.ethereum_client.w3.eth.getBalance(owner))
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        ether_data = self.ether_helper.unify_ether_badge_amounts('--ether', ether_amount)
        information_data = ' (#) Total Funds {0} '.format(ether_data)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info(' ' + STRING_DASHES)

    def command_safe_get_threshold(self, block_style=True):
        """ Command Safe Get Threshold
        This function will retrieve and show the threshold of the safe
        :param block_style:
        :return:
        """
        if block_style:
            header_data = '-:[ {0} ]:-'.format('Safe Threshold')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

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
            header_data = '-:[ {0} ]:-'.format('Safe Owners')
            self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

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
        header_data = '-:[ {0} ]:-'.format('Safe Owners List')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
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

    # def command_safe_send_ether(self, amount, address_to, approval=False):
    def command_safe_send_ether(self, address_to, wei_value):
        """ Command Safe Send Ether
        This function will perform the necessary step for properly executing the method removeOwner from the safe
        :param wei_value:
        :param address_to:
        :return:
        """
        self.logger.info('[ Previous Balance Values ]:')
        self.command_safe_get_owners()
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
