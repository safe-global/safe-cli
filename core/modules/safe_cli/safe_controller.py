#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Temporal Information Artifacts
from core.eth_assets.help_artifacts import InformationArtifacts

# Import ConsoleInputGetter for Testing Purposes
from core.input.console_input_getter import ConsoleInputGetter
from core.input.console_input_handler import ConsoleInputHandler

# Import EtherHelper for unifying ether amount quantities
from core.eth_assets.helper.ether_helper import EtherHelper

# Import Account
from eth_account import Account


class SafeController:
    """ Console Controller
    This class will represent and function as pseudo-controller for the execution of the proper commands
    :param logger:
    :param network_agent:
    :param safe_interface:
    :param ethereum_assets:
    """
    def __init__(self, logger, network_agent, safe_interface, ethereum_assets):
        self.logger = logger

        self.network_agent = network_agent

        self.ethereum_assets = ethereum_assets

        # EthereumAssets: accounts, payloads, tokens
        # Accounts:
        self.accounts = self.ethereum_assets.accounts
        # Payloads:
        self.payloads = self.ethereum_assets.payloads
        # Tokens:
        self.tokens = self.ethereum_assets.tokens

        self.console_information = InformationArtifacts(self.logger)

        # SafeInterface:
        self.safe_interface = safe_interface
        # SafeSender:
        self.safe_sender = self.safe_interface.safe_sender
        # SafeManagement:
        self.safe_management = self.safe_interface.safe_management
        # SafeEther:
        self.safe_ether = self.safe_interface.safe_ether
        # SafeToken:
        self.safe_token = self.safe_interface.safe_token
        # SafeInformation:
        self.safe_information = self.safe_interface.safe_information

        # Getter/Handler
        self.console_getter = ConsoleInputGetter(self.logger)
        self.console_handler = ConsoleInputHandler()

    def operate(self, desired_parsed_item_list, priority_group, command_argument, argument_list):
        """ Operate With Safe
        This function will operate with the safe contract_cli.log using the input command/arguments provided by the user
        :param desired_parsed_item_list:
        :param priority_group:
        :param command_argument:
        :param argument_list:
        :return:
        """
        self.logger.debug0('(+) [ Operating with Safe Console ]: ' + command_argument)

        _query, _execute, _queue, _ = self.console_getter.get_input_affix_arguments(argument_list)
        if command_argument == 'info':
            self.safe_information.view_information()
        elif command_argument == 'nonce':
            self.safe_information.view_safe_nonce()
        elif command_argument == 'code':
            self.safe_information.view_safe_code()
        elif command_argument == 'VERSION':
            self.safe_information.view_safe_version()
        elif command_argument == 'NAME':
            self.safe_information.view_safe_name()
        elif command_argument == 'getOwners':
            self.safe_information.view_safe_owners()
        elif command_argument == 'getThreshold':
            self.safe_information.view_safe_threshold()
        elif command_argument == 'isOwner':
            if priority_group == 1:
                try:
                    owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    self.safe_information.check_safe_owner(owner_address)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'areOwners':
            self.logger.info('areOwners to be Implemented')

        elif command_argument == 'changeThreshold':
            if priority_group == 1:
                try:
                    new_threshold = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    self.safe_management.change_threshold(new_threshold, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'addOwnerWithThreshold':
            if priority_group == 1:
                try:
                    new_owner_address, new_threshold = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    self.safe_management.add_owner_with_threshold(new_owner_address, new_threshold, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'addOwner':
            if priority_group == 1:
                try:
                    new_owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    self.safe_management.add_owner_with_threshold(new_owner_address, None, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'removeOwner':
            if priority_group == 1:
                try:
                    old_owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    self.safe_management.remove_owner(old_owner_address, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'removeMultipleOwners':
            self.logger.info('removeMultipleOwners to be Implemented')

        elif command_argument == 'swapOwner' or command_argument == 'changeOwner':
            if priority_group == 1:
                try:
                    old_owner_address, new_owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)

                    self.safe_management.change_owner(old_owner_address, new_owner_address, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'sendToken':
            if priority_group == 1:
                try:
                    token_address, address_to, token_amount, private_key = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    local_account = Account.privateKeyToAccount(private_key)
                    self.safe_token.send_token(
                        address_to, token_address, token_amount, local_account, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'depositToken':
            if priority_group == 1:
                try:
                    token_address, token_amount, private_key = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    local_account = Account.privateKeyToAccount(private_key)
                    self.safe_token.deposit_token(token_address, token_amount, local_account, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'withdrawToken':
            if priority_group == 1:
                try:
                    token_address, address_to, token_amount = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    self.safe_token.withdraw_token(address_to, token_address, token_amount, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'sendEther':
            if priority_group == 1:
                try:
                    address_to, private_key, ether_amounts = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    local_account = Account.privateKeyToAccount(private_key)
                    ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
                    amount = ether_helper.get_unify_ether_amount(ether_amounts)
                    self.safe_ether.send_ether(address_to, amount, local_account, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'depositEther':
            if priority_group == 1:
                try:
                    private_key, ether_amounts = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    local_account = Account.privateKeyToAccount(private_key)
                    ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
                    amount = ether_helper.get_unify_ether_amount(ether_amounts)
                    self.safe_ether.deposit_ether(amount, local_account, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'withdrawEther':
            if priority_group == 1:
                try:
                    address_to, ether_amounts = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
                    amount = ether_helper.get_unify_ether_amount(ether_amounts)
                    self.safe_ether.withdraw_ether(amount, address_to, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'changeMasterCopy':
            if priority_group == 1:
                try:
                    new_master_copy_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    self.safe_management.change_master_copy(new_master_copy_address, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        # elif command_argument == 'viewBalance':
        #     self.safe_interface.command_view_balance()
        # elif command_argument == 'viewOwners':
        #     self.safe_interface.command_view_owners()
        # elif command_argument == 'viewSender':
        #     self.safe_interface.command_view_default_sender()

        elif command_argument == 'viewNetwork':
            self.network_agent.view_networks()
        elif command_argument == 'viewAccounts':
            self.accounts.view_accounts()
        elif command_argument == 'viewPayloads':
            self.payloads.view_payloads()
        elif command_argument == 'viewTokens':
            self.tokens.view_tokens()

        elif command_argument == 'loadOwner':
            if priority_group == 1:
                private_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.safe_sender.load_owner(private_key)

        elif command_argument == 'unloadOwner':
            if priority_group == 1:
                private_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.safe_sender.unload_owner(private_key)

        elif command_argument == 'loadMultipleOwners':
            self.logger.info('load multiple owners')
        elif command_argument == 'unloadMultipleOwners':
            self.logger.info('load multiple owners')

        elif command_argument == 'setAutoFillTokenDecimals':
            self.safe_interface.command_set_auto_fill_token_decimals(argument_list[0])

        elif command_argument == 'setAutoExecute':
            self.safe_interface.command_set_auto_execute(argument_list[0])
