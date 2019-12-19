#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Import HexBytes: payloads
from hexbytes import HexBytes

# Import SafeUtils: sentinel_helper
from core.modules.safe_cli.components.safe_utils import SafeUtils


class SafeManagement:
    """ SafeManagement
    This class will give access to the management functions within the safe. This class will give change_threshold,
    add_owner, change_owner, remove_owner, update_master_copy
    :param logger:
    :param safe_interface:
    :param ethereum_assets:
    """
    def __init__(self, logger, safe_interface, ethereum_assets):
        self.name = self.__class__.__name__
        self.logger = logger

        # Formatter: view functions
        self.log_formatter = LogMessageFormatter(self.logger)

        # SafeInterface:
        self.safe_interface = safe_interface
        # SafeInstance:
        self.safe_instance = safe_interface.safe_instance
        # SafeOperator:
        self.safe_operator = safe_interface.safe_operator
        # SafeSender:
        self.safe_sender = safe_interface.safe_sender
        # SafeInformation:
        self.safe_information = safe_interface.safe_information
        # SafeTransaction:
        self.safe_transaction = safe_interface.safe_transaction

        # SafeUtils:
        self.safe_utils = SafeUtils(self.logger, self.safe_interface)

        # EthereumAssets:
        self.ethereum_assets = ethereum_assets

    def change_threshold(self, new_threshold, _execute=False, _queue=False):
        """ Command Safe Change Threshold
        This function will perform the necessary step for properly executing the method changeThreshold from the safe
        :param new_threshold:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current status of the safe before the transaction
            self.safe_information.preview_threshold_owners()

            # Sender payload data
            sender_data = self.safe_transaction.safe_tx_sender_payload()

            # Generating the function payload data
            payload_data = HexBytes(self.safe_instance.functions.changeThreshold(
                new_threshold).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            if self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue):
                # Preview the current status of the safe after the transaction
                self.safe_information.preview_threshold_owners()

        except Exception as err:
            self.logger.error('Unable to command_safe_change_threshold(): {0} {1}'.format(type(err), err))

    def add_owner_with_threshold(self, new_owner_address, new_threshold=None, _execute=False, _queue=False):
        """ Command Safe Change Threshold
        This function will perform the necessary step for properly executing the method addOwnerWithThreshold
         from the safe
        :param new_owner_address:
        :param new_threshold:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current status of the safe before the transaction
            self.safe_information.preview_threshold_owners()

            # Sender payload data
            sender_data = self.safe_transaction.safe_tx_sender_payload()

            # If threshold is not set, make a increment of 1
            if new_threshold is None:
                new_threshold = self.safe_operator.retrieve_threshold() + 1

            # If new value is higher than the current number of owners + 1 the transaction will not be performed <>
            elif (self.safe_operator.retrieve_threshold() + 1) < new_threshold:
                self.logger.error('Invalid Threshold Amount')
                return

            # Pack function payload data
            payload_data = HexBytes(self.safe_instance.functions.addOwnerWithThreshold(
                new_owner_address, new_threshold).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data.hex())

            # Perform the transaction
            if self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue):
                # Preview the current status of the safe after the transaction
                self.safe_information.preview_threshold_owners()

        except Exception as err:
            self.logger.error('Unable to command_safe_add_owner_threshold(): {0} {1}'.format(type(err), err))

    def change_owner(self, owner_address, new_owner_address, _execute=False, _queue=False):
        """ Command Safe Swap Owner | Change Owner
        This function will perform the necessary step for properly executing the method swapOwners from the safe
        :param owner_address:
        :param new_owner_address:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            previous_owner = self.safe_utils.setinel_helper(owner_address)
            # Preview the current status of the safe before the transaction
            self.safe_information.preview_threshold_owners()

            # Sender payload data
            sender_data = self.safe_transaction.safe_tx_sender_payload()

            # Pack function payload data
            payload_data = HexBytes(self.safe_instance.functions.swapOwner(
                str(previous_owner), str(owner_address), str(new_owner_address)).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data.hex())

            # Perform the transaction
            if self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue):
                # Lastly since there is a new owner registered within the safe, the sender should be recalculated
                self.safe_sender.unload_owner_via_address(owner_address)
                # Preview the current status of the safe after the transaction
                self.safe_information.preview_threshold_owners()
        except Exception as err:
            self.logger.error('Unable to command_safe_swap_owner(): {0} {1}'.format(type(err), str(err)))

    def remove_owner(self, owner_address, _execute=False, _queue=False):
        """ Command Safe Change Threshold
        This function will perform the necessary step for properly executing the method removeOwner from the safe
        :param owner_address:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            previous_owner_address = self.safe_utils.setinel_helper(owner_address)

            # Preview the current status of the safe before the transaction
            self.safe_information.preview_threshold_owners()

            # Sender payload data
            sender_data = self.safe_transaction.safe_tx_sender_payload()

            if self.safe_operator.retrieve_threshold() >= 2:
                new_threshold = self.safe_operator.retrieve_threshold() - 1
            else:
                new_threshold = self.safe_operator.retrieve_threshold()

            # Generating the function payload data
            self.logger.info('| Sender: {0} | Previous Owner: {1} | Owner to Remove: {2} | Threshold: {3} | '.format(
                self.safe_sender.sender_address, previous_owner_address, owner_address, int(new_threshold)))
            self.log_formatter.log_dash_splitter()

            # Pack function payload data
            payload_data = HexBytes(self.safe_instance.functions.removeOwner(
                previous_owner_address, owner_address, int(new_threshold)).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data.hex())

            # Perform the transaction
            if self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue):
                # Lastly since there is a new owner registered within the safe, the sender should be recalculated
                self.safe_sender.unload_owner_via_address(owner_address)
                # Preview the current status of the safe after the transaction
                self.safe_information.preview_threshold_owners()
        except Exception as err:
            self.logger.error('Unable to command_safe_remove_owner(): {0} {1}'.format(type(err), err))

    def change_master_copy(self, new_master_copy_address, _execute=False, _queue=False):
        """ Command Safe Change MasterCopy
        This function will perform the necessary step for properly executing the method changeMasterCopy from the safe
        :param new_master_copy_address:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current status of the safe version before the transaction
            self.safe_information.preview_version_change()

            # Sender payload data
            sender_data = self.safe_transaction.safe_tx_sender_payload()

            # Pack function payload data
            payload_data = HexBytes(self.safe_instance.functions.changeMasterCopy(
                new_master_copy_address).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data.hex())

            # Perform the transaction
            if self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue):
                # Preview the current status of the safe version after the transaction
                self.safe_information.preview_version_change()

        except Exception as err:
            self.logger.error('Unable to command_safe_change_version(): {0} {1}'.format(type(err), err))
