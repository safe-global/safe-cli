#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Temporal Information Artifacts
from core.artifacts.help_artifacts import InformationArtifacts

# Import ConsoleInputGetter for Testing Purposes
from core.input.console_input_getter import ConsoleInputGetter
from core.input.console_input_handler import ConsoleInputHandler

# Import EtherHelper for unifying ether amount quantities
from core.artifacts.utils.ether_helper import EtherHelper

# Import Account
from eth_account import Account


class ConsoleController:
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

    def operate_with_console(self, desired_parsed_item_list, priority_group, command_argument, argument_list):
        """ Operate With Console
        This function will operate with the gnosis console using the input command/arguments provided by the user
        :param desired_parsed_item_list:
        :param priority_group:
        :param command_argument:
        :param argument_list:
        :return:
        """
        # load console console commands trigger procedures
        self.logger.debug0('(+) [ Operating with General Console ]: ' + command_argument)
        if command_argument == 'loadContract':
            if priority_group == 0:
                contract_alias = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.contract_interface = self.console_engine.run_contract_console(contract_alias)
        elif command_argument == 'loadSafe':
            if priority_group == 1:
                safe_address = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.safe_interface = self.console_engine.run_safe_console(safe_address)

        # view console commands procedures
        elif command_argument == 'viewTokens':
            self.token_artifacts.command_view_tokens()
        elif command_argument == 'viewNetwork':
            self.network_agent.command_view_networks()
        elif command_argument == 'viewContracts':
            self.contract_artifacts.command_view_contracts()
        elif command_argument == 'viewAccounts':
            self.account_artifacts.command_view_accounts()
        elif command_argument == 'viewPayloads':
            self.payload_artifacts.command_view_payloads()

        # new console commands trigger procedures
        elif command_argument == 'newAccount':
            self.logger.info('newAccount <Address> or <PK> or <PK + Address>')
        elif command_argument == 'newPayload':
            self.payload_artifacts.command_new_payload(command_argument, argument_list)
        elif command_argument == 'newTxPayload':
            self.payload_artifacts.command_new_payload(command_argument, argument_list)
        elif command_argument == 'newToken':
            self.token_artifacts.command_new_token(command_argument, argument_list)

        # setter console commands trigger procedures
        elif command_argument == 'setNetwork':
            if priority_group == 1:
                network_name, network_api_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.network_agent.set_network_provider_endpoint(network_name, network_api_key)
            elif priority_group == 2:
                network_name, network_api_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.network_agent.set_network_provider_endpoint(network_name, network_api_key)

        # information console commands trigger procedures
        elif command_argument == 'about':
            self.console_information.command_view_about()
        elif command_argument == 'help':
            self.console_information.command_view_general_information()

    def operate_with_safe(self, desired_parsed_item_list, priority_group, command_argument, argument_list, safe_interface):
        """ Operate With Safe
        This function will operate with the safe contract using the input command/arguments provided by the user
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
            safe_interface.command_safe_nonce()
        elif command_argument == 'code':
            safe_interface.command_safe_code()
        elif command_argument == 'VERSION':
            safe_interface.command_safe_version()
        elif command_argument == 'NAME':
            safe_interface.command_safe_name()
        elif command_argument == 'getOwners':
            safe_interface.command_safe_get_owners()
        elif command_argument == 'getThreshold':
            safe_interface.command_safe_get_threshold()
        elif command_argument == 'isOwner':
            if priority_group == 1:
                try:
                    owner_address = self.console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
                    safe_interface.command_safe_is_owner(owner_address)
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
                safe_interface.command_load_owner(private_key)

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

        elif command_argument == 'setBaseGas':
            safe_interface.command_set_base_gas(argument_list[0])

        elif command_argument == 'setSafeTxGas':
            safe_interface.command_set_safe_tx_gas(argument_list[0])

        elif command_argument == 'viewGas':
            safe_interface.command_view_gas()

    def operate_with_contract(self, stream, contract_methods, contract_instance):
        """ Operate With Contract
        This function will retrieve the methods present in the contract_instance
        :param stream: command_argument (method to call) that will trigger the operation
        :param contract_methods: dict with all the avaliable methods retrieved from the abi file
        :param contract_instance: only for eval() so it can be triggered
        :return: if method found, a method from the current contract will be triggered, success or
        not depends on the establishing of the proper values.
        """
        try:
            self.logger.debug0('(+) [ Operating with Contract Console ]: ' + stream)
            for item in contract_methods:
                if contract_methods[item]['name'] in stream:
                    splitted_stream = stream.split(' ')
                    address_from = ''
                    # This function Call now longer works, break in compatibility
                    _query, _execute, _queue, _ = self.console_getter.get_input_affix_arguments(splitted_stream)
                    function_name, function_arguments = \
                        self.console_getter.retrieve_contract_data(splitted_stream, contract_methods[item]['arguments'])
                    self.logger.debug0('command: {0} | arguments: {1} | execute_flag: {2} | query_flag: {3} | '.format(
                        function_name, function_arguments, _execute, _queue))

                    if _execute or _queue or _query:
                        if _query:
                            # remark: Call Solver
                            self.logger.info(contract_methods[item]['call'].format(function_arguments, address_from))
                            resolution = eval(contract_methods[item]['call'].format(function_arguments, address_from))
                            self.logger.info(resolution)

                        elif _execute:
                            # remark: Transaction Solver
                            if contract_methods[item]['name'].startswith('get'):
                                self.logger.warn('transact() operation is discourage if you are using a getter method')
                            # if address_from != '':
                                # address_from = '\{\'from\':{0}\}'.format(address_from)

                            self.logger.info(contract_methods[item]['transact'].format(function_arguments, address_from))
                            resolution = eval(contract_methods[item]['transact'].format(function_arguments, address_from))
                            self.logger.info(resolution)
                            # this is the hash to be signed, maybe call for approve dialog, approveHash dialogue,
                            # map functions to be performed by the gnosis_py library

                        elif _queue:
                            # remark: Add to the Batch Solver
                            self.logger.info('(Future Implementation) executeBatch when you are ready to launch '
                                             'the transactions that you queued up!')

                    else:
                        self.logger.warn('--execute, --query or --queue arguments needed in order to properly '
                                         'operate with the current contract')

        except Exception as err:
            self.logger.debug0('operate_with_contract() {0}'.format(err))
