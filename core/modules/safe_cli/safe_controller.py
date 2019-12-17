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
    """
    def __init__(self, logger, network_agent, data_artifact, console_engine):
        self.logger = logger

        self.data_artifact = data_artifact
        self.contract_artifacts = self.data_artifact.contract_artifacts
        self.account_artifacts = self.data_artifact.account_artifacts
        self.payload_artifacts = self.data_artifact.payload_artifacts
        self.token_artifacts = self.data_artifact.token_artifacts
        self.network_agent = network_agent
        self.console_information = InformationArtifacts(self.logger)

        self.console_engine = console_engine
        self.safe_interface = None
        self.contract_interface = None
        self.console_getter = ConsoleInputGetter(self.logger)
        self.console_handler = ConsoleInputHandler(self.logger, self.data_artifact)

    def operate_with_safe(self, desired_parsed_item_list, priority_group, command_argument, argument_list, safe_interface):
        """ Operate With Safe
        This function will operate with the safe contract_cli using the input command/arguments provided by the user
        :param desired_parsed_item_list:
        :param priority_group:
        :param command_argument:
        :param argument_list:
        :param safe_interface:
        :return:
        """
        self.logger.debug0('(+) [ Operating with Safe Console ]: ' + command_argument)
        _query, _execute, _queue, _ = self.console_getter.get_input_affix_arguments(argument_list)
        if command_argument == 'info':
            safe_interface.command_safe_information()
        elif command_argument == 'help':
            self.console_information.command_view_safe_information()
        elif command_argument == 'nonce':
            safe_interface.view_safe_nonce()
        elif command_argument == 'code':
            safe_interface.view_safe_code()
        elif command_argument == 'VERSION':
            safe_interface.view_safe_version()
        elif command_argument == 'NAME':
            safe_interface.view_safe_name()
        elif command_argument == 'getOwners':
            safe_interface.view_safe_owners()
        elif command_argument == 'getThreshold':
            safe_interface.view_safe_threshold()
        elif command_argument == 'isOwner':
            if priority_group == 1:
                try:
                    owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    safe_interface.check_safe_owner(owner_address)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'areOwners':
            self.logger.info('areOwners to be Implemented')

        elif command_argument == 'changeThreshold':
            if priority_group == 1:
                try:
                    new_threshold = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    safe_interface.command_safe_change_threshold(new_threshold, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'addOwnerWithThreshold':
            if priority_group == 1:
                try:
                    new_owner_address, new_threshold = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    safe_interface.command_safe_add_owner_threshold(new_owner_address, new_threshold, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'addOwner':
            if priority_group == 1:
                try:
                    new_owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    safe_interface.command_safe_add_owner_threshold(new_owner_address, None, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'removeOwner':
            if priority_group == 1:
                try:
                    old_owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    previous_owner_address = safe_interface.setinel_helper(old_owner_address)
                    safe_interface.command_safe_remove_owner(
                        previous_owner_address, old_owner_address, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'removeMultipleOwners':
            self.logger.info('removeMultipleOwners to be Implemented')

        elif command_argument == 'swapOwner' or command_argument == 'changeOwner':
            if priority_group == 1:
                try:
                    old_owner_address, new_owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    previous_owner_address = safe_interface.setinel_helper(old_owner_address)
                    safe_interface.command_safe_swap_owner(
                        previous_owner_address, old_owner_address, new_owner_address, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'sendToken':
            if priority_group == 1:
                try:
                    token_address, address_to, token_amount, private_key = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    local_account = Account.privateKeyToAccount(private_key)
                    safe_interface.command_send_token(
                        address_to, token_address, token_amount, local_account, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'depositToken':
            if priority_group == 1:
                try:
                    token_address, token_amount, private_key = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    local_account = Account.privateKeyToAccount(private_key)
                    safe_interface.command_deposit_token(token_address, token_amount, local_account, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'withdrawToken':
            if priority_group == 1:
                try:
                    token_address, address_to, token_amount = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    safe_interface.command_withdraw_token(address_to, token_address, token_amount, _execute, _queue)
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
                    safe_interface.command_send_ether(address_to, amount, local_account, _execute, _queue)
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
                    safe_interface.command_deposit_ether(amount, local_account, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'withdrawEther':
            if priority_group == 1:
                try:
                    address_to, ether_amounts = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
                    amount = ether_helper.get_unify_ether_amount(ether_amounts)
                    safe_interface.command_withdraw_ether(amount, address_to, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'updateSafe':
            if priority_group == 1:
                try:
                    new_master_copy_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    safe_interface.command_safe_change_version(new_master_copy_address, _execute, _queue)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'viewBalance':
            safe_interface.command_view_balance()
        elif command_argument == 'viewOwners':
            safe_interface.command_view_owners()
        elif command_argument == 'viewSender':
            safe_interface.command_view_default_sender()
        elif command_argument == 'viewNetwork':
            self.network_agent.command_view_networks()
        elif command_argument == 'viewContracts':
            self.contract_artifacts.command_view_contracts()
        elif command_argument == 'viewAccounts':
            self.account_artifacts.command_view_accounts()
        elif command_argument == 'viewPayloads':
            self.payload_artifacts.command_view_payloads()
        elif command_argument == 'viewTokens':
            self.token_artifacts.command_view_tokens()
        elif command_argument == 'loadOwner':
            if priority_group == 1:
                private_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                safe_interface.load_owner(private_key)

        elif command_argument == 'unloadOwner':
            if priority_group == 1:
                private_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                safe_interface.command_unload_owner(private_key)

        elif command_argument == 'loadMultipleOwners':
            self.logger.info('load multiple owners')
        elif command_argument == 'unloadMultipleOwners':
            self.logger.info('load multiple owners')

        elif command_argument == 'setAutoFillTokenDecimals':
            safe_interface.command_set_auto_fill_token_decimals(argument_list[0])

        elif command_argument == 'setAutoExecute':
            safe_interface.command_set_auto_execute(argument_list[0])
