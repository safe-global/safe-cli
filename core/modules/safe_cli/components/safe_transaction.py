#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Exceptions: _add, _remove operations
from core.modules.safe_cli.exceptions.safe_sender_exceptions import SafeSenderNotEnoughSigners

# Import Log Formatter: Receipts, Headers
from core.logger.log_message_formatter import LogMessageFormatter

# Constants
from core.constants.console_constant import NULL_ADDRESS

# Import HexBytes Module
from hexbytes import HexBytes

# Import Gnosis-Py Modules
from gnosis.safe.safe import SafeOperation

# execution_type = query, queue, execute


class SafeTransaction:
    """ Console Safe Commands
    This class will perform the command call to the different eth_assets and the class methods
    :param logger:
    :param network_agent:
    :param safe_interface:
    :param safe_configuration:
    """
    def __init__(self, logger, network_agent, safe_interface):
        self.logger = logger

        # NetworkAgent: None
        self.network_agent = network_agent
        self.ethereum_client = network_agent.ethereum_client

        # Setup: LogFormatter
        self.log_formatter = LogMessageFormatter(self.logger)

        # SafeInterface:
        self.safe_interface = safe_interface
        # SafeInstance:
        self.safe_instance = self.safe_interface.safe_instance
        # SafeSender:
        self.safe_sender = self.safe_interface.safe_sender
        # SafeOperator:
        self.safe_operator = self.safe_interface.safe_operator
        # SafeConfiguration:
        self.safe_configuration = self.safe_interface.safe_configuration

        # Default gas values until gasStation is integrated
        self.safe_tx_gas = 300000
        self.base_gas = 200000

        # Due to an unknow issue in Safe(), in ganache network gasPrice it's set to 0, otherwise the tx does not execute
        self.gas_price = self.fix_gas_price()

        # Transaction Queue for Batching
        self.tx_queue = []

    def fix_gas_price(self):
        """ Fix_Gas_Price
        This function will restrict the gas price to 0 if ganache network is detected
        """
        if self.network_agent.network == 'ganache':
            return 0
        return self.ethereum_client.w3.eth.gasPrice

    def safe_tx_sender_payload(self):
        """ Safe_Tx_Sender_Payload
        This functions will setup the safe_tx payload sender to be used while running perform_transaction
        :return:
        """
        return {'from': self.safe_sender.sender_address, 'gas': self.base_gas, 'gasPrice': self.gas_price}

    def safe_tx_multi_sign(self, safe_tx):
        """ Safe Tx Multi Sign
        This function will perform the sign for every member in the signer_list to the current safe_tx
        :param safe_tx:
        :return:
        """
        try:
            self.log_formatter.log_section_left_side('Multi Signature')
            if self.safe_sender.are_enough_signatures_loaded():
                for signer in self.safe_sender.sender_account_list:
                    safe_tx.sign(signer.privateKey)
                    self.log_formatter.log_data(' (#) Owner Address: {0}', signer.address)
                    self.log_formatter.log_data(' (#) Sign with Private Key: {0}', HexBytes(signer.privateKey).hex())
                    self.log_formatter.log_dash_splitter()
                return safe_tx

        except SafeSenderNotEnoughSigners:
            raise SafeSenderNotEnoughSigners(None)
        except Exception as err:
            self.logger.error('Unexpected error in multi_sign_safe_tx(): {0} {1}'.format(type(err), err))

    def safe_tx_multi_approve(self, safe_tx):
        """ Safe Tx Multi Approve
        This function will perform an approval for every member in the signer_list to the current safe_tx
        :param safe_tx:
        :return:
        """
        try:
            self.log_formatter.log_section_left_side('Multi Approval')
            if self.safe_sender.are_enough_signatures_loaded():
                for signer in self.safe_sender.sender_account_list:
                    # bug: Approve
                    self.log_formatter.log_data(' (#) Owner Address: {0}', signer.address)
                    self.log_formatter.log_data(' (#) Approving Tx with Hash: {0}', HexBytes(safe_tx.safe_tx_hash).hex())
                    self.log_formatter.log_dash_splitter()

        except SafeSenderNotEnoughSigners:
            raise SafeSenderNotEnoughSigners(None)
        except Exception as err:
            self.logger.error('Unexpected error in safe_tx_multi_approve(): {0} {1}'.format(type(err), err))

    def _setup_safe_tx_values(self, address_to, wei_value):
        """ Setup_Safe_Tx_Values
        This function will set default values for address_to & wei_value if they are not pass to perform_transaction
        :param address_to:
        :param wei_value:
        :return: Default values for address_to/wei_value, otherwise return 0 and safe_operator.safe_instance.address
        """
        if wei_value is None:
            wei_value = 0
        if address_to is None:
            address_to = self.safe_instance.address
        return address_to, wei_value

    def perform_transaction(self, payload_data, wei_value=None, address_to=None, _execute=False, _queue=False):
        """ Perform_Transaction
        This function will perform the transaction to the safe we have currently triggered via console command
        :param payload_data:
        :param wei_value:
        :param address_to:
        :param _execute:
        :param _queue:
        :return: Return True if safe_tx is perform, otherwise False
        """
        safe_tx_receipt = None
        address_to, wei_value = self._setup_safe_tx_values(address_to, wei_value)
        try:
            # Retrieve safe nonce
            safe_nonce = self.safe_operator.retrieve_nonce()

            # Create the safe_tx
            safe_tx = self.safe_operator.build_multisig_tx(
                address_to, wei_value, payload_data, SafeOperation.CALL.value,
                self.safe_tx_gas, self.base_gas, self.fix_gas_price(),
                NULL_ADDRESS, NULL_ADDRESS, b'', safe_nonce=safe_nonce)

            # Multi sign the safe_tx
            safe_tx = self.safe_tx_multi_sign(safe_tx)

            if self._is_valid_tx(safe_tx):
                if self.safe_configuration.auto_execute or _execute:
                    # Execute the safe_tx if AutoExecute or --execute was used
                    safe_tx_hash, _ = safe_tx.execute(
                        self.safe_sender.sender_private_key,
                        tx_gas=self.base_gas + self.safe_tx_gas,
                        tx_gas_price=self.fix_gas_price())

                    # Retrieve the receipt
                    safe_tx_receipt = self.ethereum_client.get_transaction_receipt(safe_tx_hash, timeout=60)
                    self.log_formatter.tx_receipt_formatter(safe_tx_receipt, detailed_receipt=True)
                    return True

                elif _queue:
                    # Queue the safe_tx if --queue was used
                    self.logger.info('Tx Added to Batch Queue')
                    self.tx_queue.append(safe_tx)

            return False
        except SafeSenderNotEnoughSigners as err:
            self.logger.error(err.message)

        except Exception as err:
            self.logger.error('Unexpected error in perform_transaction(): {0} {1}'.format(type(err), err))

    def _is_valid_tx(self, safe_tx):
        """ Is_Valid_Tx
        This function will make a call, to verify the current tx, if valid this function will return true, otherwise
        it will throw exceptions InvalidTx.
        """
        is_valid_tx = safe_tx.call()
        if is_valid_tx:
            # The current safe_tx is properly form
            self.log_formatter.log_data(' (#) isValid Tx: {0}', is_valid_tx)
            self.log_formatter.log_dash_splitter()
            return True
        return False
