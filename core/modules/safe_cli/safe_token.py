#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Import Constants: view_fall_back_handler
from core.constants.console_constant import NULL_ADDRESS

# Import HexBytes Module: view_code in hex
from hexbytes import HexBytes


class SafeToken:
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

    def send_token(self, address_to, token_address, token_amount, local_account, _execute=False, _queue=False):
        """ Command Send Token
        This function will send tokens
        :param address_to:
        :param token_address:
        :param token_amount:
        :param local_account:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current token balance of the safe before the transaction
            self.command_view_token_balance()
            self.log_formatter.log_section_left_side('Send Token')
            erc20 = get_erc20_contract(self.ethereum_client.w3, token_address)
            if self.auto_fill_token_decimals:
                token_amount = (token_amount * pow(10, erc20.functions.decimals().call()))

            if _execute:
                safe_tx = self.ethereum_client.erc20.send_tokens(
                    address_to, token_amount, token_address, local_account.privateKey)

                # Perform the transaction
                tx_receipt = self.ethereum_client.get_transaction_receipt(safe_tx, timeout=60)

                # Format Receipt with Logger
                self.log_formatter.tx_receipt_formatter(tx_receipt, detailed_receipt=True)

            elif _queue:
                # remark: Since the send resolves the current transaction, the current step needs a work around
                self.tx_queue.append('sendToken')

            # Preview the current token balance of the safe after the transaction
            self.command_view_token_balance()
        except Exception as err:
            self.logger.error('Unable to command_send_token_raw(): {0} {1}'.format(type(err), err))


    def deposit_token(self, token_address, token_amount, local_account, _execute=False, _queue=False):
        """ Command Deposit Token
        This function will deposit tokens from the safe
        :param token_address:
        :param token_amount:
        :param local_account:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            self.command_send_token(address_to=self.safe_operator.address, token_address=token_address,
                                    token_amount=token_amount, local_account=local_account,
                                    _execute=_execute, _queue=_queue)
        except Exception as err:
            self.logger.error('Unable to command_deposit_token_raw(): {0} {1}'.format(type(err), err))


    def withdraw_token(self, address_to, token_address, token_amount, _execute=False, _queue=False):
        """ Command Withdraw Token
        This function will withdraw tokens from the safe
        :param address_to:
        :param token_address:
        :param token_amount:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current token balance of the safe before the transaction
            self.command_view_token_balance()
            sender_data = {'from': self.safe_operator.address}
            erc20 = get_erc20_contract(self.ethereum_client.w3, token_address)
            if self.auto_fill_token_decimals:
                token_amount = (token_amount * pow(10, erc20.functions.decimals().call()))

            payload_data = HexBytes(erc20.functions.transfer(
                address_to, token_amount).buildTransaction(sender_data)['data'])

            # Perform the transaction
            self.perform_transaction(payload_data, address_to=token_address, _execute=_execute, _queue=_queue)

            # Preview the current token balance of the safe after the transaction
            current_token_balance = self.ethereum_client.erc20.get_balance(self.safe_operator.address,
                                                                           token_address)
            current_user_balance = self.ethereum_client.erc20.get_balance(self.safe_operator.address,
                                                                          token_address)
            self.logger.debug0(current_token_balance)
            self.logger.debug0(current_user_balance)
            self.command_view_token_balance()
        except Exception as err:
            self.logger.error('Unable to command_withdraw_token_raw(): {0} {1}'.format(type(err), err))


    def view_token_balance(self):
        """ Command View Token Balance
        This function will sho the token balance of known tokens
        """
        try:
            self.log_formatter.log_section_left_side('Safe Token Balance')
            token_address = []
            token_symbol = []
            for token_item in self.token_artifacts.token_data:
                current_token_address = self.token_artifacts.token_data[token_item]['address']
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
                    information_data = ' (#) Total Safe {0} ({1}) Funds: {2} Token'.format(
                        current_name_to_show, item['token_address'], item['balance'])
                    self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
            self.logger.info(' ' + STRING_DASHES)
        except Exception as err:
            self.logger.error('Unable to command_view_token_balance(): {0} {1}'.format(type(err), err))