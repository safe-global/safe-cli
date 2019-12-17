#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Import HexBytes: payloads
from hexbytes import HexBytes


class SafeManagement:
    def __init__(self, logger, safe_interface, safe_sender, safe_information, safe_transaction):
        self.name = self.__class__.__name__
        self.logger = logger

        self.safe_interface = safe_interface
        self.safe_sender = safe_sender
        self.safe_information = safe_information
        self.safe_transaction = safe_transaction

        # Formatter: view functions
        self.log_formatter = LogMessageFormatter(self.logger)

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
            payload_data = HexBytes(self.safe_interface.functions.changeThreshold(
                new_threshold).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue)

            # Preview the current status of the safe after the transaction
            self.safe_information.preview_threshold_owners()

        except Exception as err:
            self.logger.error('Unable to command_safe_change_threshold(): {0} {1}'.format(type(err), err))

    def add_owner_threshold(self, new_owner_address, new_threshold=None, _execute=False, _queue=False):
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
                new_threshold = self.safe_interface.retrieve_threshold() + 1

            # If new value is higher than the current number of owners + 1 the transaction will not be performed <>
            elif (self.safe_interface.retrieve_threshold() + 1) < new_threshold:
                self.logger.error('Invalid Threshold Amount')
                return

            # Pack function payload data
            payload_data = HexBytes(self.safe_interface.functions.addOwnerWithThreshold(
                new_owner_address, new_threshold).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue)

            # Preview the current status of the safe after the transaction
            self.safe_information.preview_threshold_owners()

            # Lastly since there is a new owner registered within the safe, the sender should be recalculated
        except Exception as err:
            self.logger.error('Unable to command_safe_add_owner_threshold(): {0} {1}'.format(type(err), err))

    def change_owner(self, previous_owner, owner, new_owner, _execute=False, _queue=False):
        """ Command Safe Swap Owner | Change Owner
        This function will perform the necessary step for properly executing the method swapOwners from the safe
        :param previous_owner:
        :param owner:
        :param new_owner:
        :param _execute:
        :param _queue:
        :return:
        """
        # give list of owners and get the previous owner
        try:
            # Preview the current status of the safe before the transaction
            self.safe_information.preview_threshold_owners()

            # Sender payload data
            sender_data = self.safe_transaction.safe_tx_sender_payload()

            # Pack function payload data
            payload_data = HexBytes(self.safe_interface.functions.swapOwner(
                str(previous_owner), str(owner), str(new_owner)).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue)

            # Preview the current status of the safe after the transaction
            self.safe_information.preview_threshold_owners()
        except Exception as err:
            self.logger.error('Unable to command_safe_swap_owner(): {0} {1}'.format(type(err), str(err)))

    def remove_owner(self, previous_owner_address, owner_address, _execute=False, _queue=False):
        """ Command Safe Change Threshold
        This function will perform the necessary step for properly executing the method removeOwner from the safe
        :param previous_owner_address:
        :param owner_address:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current status of the safe before the transaction
            self.safe_information.preview_threshold_owners()

            # Sender payload data
            sender_data = self.safe_transaction.safe_tx_sender_payload()

            if self.safe_interface.retrieve_threshold() >= 2:
                new_threshold = self.safe_interface.retrieve_threshold() - 1
            else:
                new_threshold = self.safe_interface.retrieve_threshold()

            # Generating the function payload data

            self.logger.info('| Sender: {0} | Previous Owner: {1} | Owner to Remove: {2} | Threshold: {3} | '.format(
                self.safe_sender.sender_address, previous_owner_address, owner_address, int(new_threshold)))
            self.log_formatter.log_dash_splitter()

            # Pack function payload data
            payload_data = HexBytes(self.safe_interface.functions.removeOwner(
                previous_owner_address, owner_address, int(new_threshold)).buildTransaction(sender_data)['data'])
            self.log_formatter.tx_data_formatter(sender_data, payload_data.hex())

            # Perform the transaction
            self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue)

            # Preview the current status of the safe after the transaction
            self.safe_information.preview_threshold_owners()

            # Lastly since there is a new owner registered within the safe, the sender should be recalculated
        except Exception as err:
            self.logger.error('Unable to command_safe_remove_owner(): {0} {1}'.format(type(err), err))

    def change_version(self, address_version, _execute=False, _queue=False):
        """ Command Safe Change MasterCopy
        This function will perform the necessary step for properly executing the method changeMasterCopy from the safe
        :param address_version:
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
            payload_data = HexBytes(self.safe_interface.functions.changeMasterCopy(
                address_version).buildTransaction(sender_data)['data']).hex()
            self.log_formatter.tx_data_formatter(sender_data, payload_data)

            # Perform the transaction
            self.safe_transaction.perform_transaction(payload_data, _execute=_execute, _queue=_queue)

            # Preview the current status of the safe version after the transaction
            self.safe_information.preview_version_change()
        except Exception as err:
            self.logger.error('Unable to command_safe_change_version(): {0} {1}'.format(type(err), err))
