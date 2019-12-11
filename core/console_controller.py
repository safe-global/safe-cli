#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Temporal Information Artifacts
from core.artifacts.help_artifacts import InformationArtifacts

# Import ConsoleInputGetter for Testing Purposes
from core.input.console_input_getter import ConsoleInputGetter

# Import HexBytes Module
from hexbytes import HexBytes
from core.artifacts.utils.ether_helper import EtherHelper
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
        self.console_information = InformationArtifacts()

        self.console_engine = console_engine
        self.safe_interface = None
        self.contract_interface = None
        self.console_getter = ConsoleInputGetter(self.logger)

    def operate_with_console(self, desired_parsed_item_list, priority_group, command_argument, argument_list):
        """ Operate With Console
        This function will operate with the gnosis console using the input command/arguments provided by the user
        :param desired_parsed_item_list:
        :param priority_group:
        :param command_argument:
        :param argument_list:
        :param console_session:
        :return:
        """
        # load console console commands trigger procedures
        self.logger.debug0('(+) [ Operating with General Console ]: ' + command_argument)
        if command_argument == 'loadContract':
            self.contract_interface = self.console_engine.run_contract_console(desired_parsed_item_list, priority_group)
        elif command_argument == 'loadSafe':
            self.safe_interface = self.console_engine.run_safe_console(desired_parsed_item_list, priority_group)

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
            self.logger.info('newToken <Address>')

        # setter console commands trigger procedures
        elif command_argument == 'setNetwork':
            if priority_group == 1:
                network = desired_parsed_item_list[0][1][0]
                print(network)
                self.network_agent.set_network_provider_endpoint(network, None)
            elif priority_group == 2:
                print(desired_parsed_item_list)
                network = desired_parsed_item_list[0][1][0]
                api_key = desired_parsed_item_list[1][1][0]
                print(network, api_key)
                self.network_agent.set_network_provider_endpoint(network, api_key)
        elif command_argument == 'setAutofill':
            self.logger.info('Autofill option to be implemented')

        # information console commands trigger procedures
        elif command_argument == 'about':
            self.console_information.command_view_about()
        elif (command_argument == 'info') or (command_argument == 'help'):
            self.console_information.command_view_help()

        # test console getter commands trigger procedures
        elif command_argument == 'dummyCommand':
            #self.console_getter.get_gnosis_input_command_argument(stream)
            self.logger.info('do nothing')

    def setinel_helper(self, address_value, safe_interface):
        """ Sender Helper
        This function send utils
        :param address_value:
        :param safe_interface:
        :return:
        """
        previous_owner = '0x' + ('0' * 39) + '1'
        self.logger.info('[ Current Owner with Address to be Removed ]: {0}'.format(str(address_value)))
        self.logger.info('[ Current Local Account Owners ]: {0}'.format(safe_interface.safe_operator.retrieve_owners()))
        for index, owner_address in enumerate(safe_interface.safe_operator.retrieve_owners()):
            if address_value == owner_address:
                self.logger.info('[ Found Owner in Owners ]: {0} with Index {1}'.format(owner_address, index))
                try:
                    sentinel_index = (index - 1)
                    self.logger.info('[ SENTINEL Address Index ]: {0}'.format(sentinel_index))
                    if index != 0:
                        current_owner_list = safe_interface.safe_operator.retrieve_owners()
                        previous_owner = current_owner_list[(index - 1)]

                    self.logger.info('[ Found PreviousOwner on the list ]: {0}'.format(previous_owner))
                    return previous_owner
                except IndexError:
                    self.logger.error('Sentinel Address not found, returning NULLADDRESS')

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
        # Commands to be implemented:
        # - updateSafe: evaluate if current version can be uploaded to the newest one
        self.logger.debug0('(+) [ Operating with Safe Console ]: ' + command_argument)
        if command_argument == 'info':
            safe_interface.command_safe_information()
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
                    address_value_to = desired_parsed_item_list[0][1][0]
                    safe_interface.command_safe_is_owner(str(address_value_to))
                except Exception as err:
                    self.logger.error(err)
            elif priority_group == -1:
                self.logger.info('isOwner --address=0x')

        elif command_argument == 'areOwners':
            self.logger.info('areOwners to be Implemented')

        elif command_argument == 'changeThreshold':
            if priority_group == 1:
                try:
                    uint_value = desired_parsed_item_list[0][1][0]
                    safe_interface.command_safe_change_threshold(int(uint_value))
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'addOwnerWithThreshold':
            if priority_group == 1:
                try:
                    address_value_to = desired_parsed_item_list[0][1][0]
                    uint_value = desired_parsed_item_list[1][1][0]
                    safe_interface.command_safe_add_owner_threshold(str(address_value_to), int(uint_value))
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'addOwner':
            if priority_group == 1:
                try:
                    address_value_to = desired_parsed_item_list[0][1][0]
                    safe_interface.command_safe_add_owner_threshold(address_value_to)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'removeOwner':
            if priority_group == 1:
                try:
                    address_value_to = desired_parsed_item_list[0][1][0]
                    previous_owner = self.setinel_helper(address_value_to, safe_interface)
                    safe_interface.command_safe_remove_owner(str(previous_owner), str(address_value_to))
                except Exception as err:
                    self.logger.info(err)

        elif command_argument == 'removeMultipleOwners':
            self.logger.info('removeMultipleOwners to be Implemented')

        elif command_argument == 'swapOwner' or command_argument == 'changeOwner':
            if priority_group == 1:
                try:
                    address_value_to = desired_parsed_item_list[0][1][0]
                    address_new_value = desired_parsed_item_list[0][1][1]
                    previous_owner = self.setinel_helper(address_value_to, safe_interface)
                    safe_interface.command_safe_swap_owner(previous_owner, address_value_to, address_new_value)
                except Exception as err:
                    print(type(err), err)

        elif command_argument == 'sendToken':
            if priority_group == 1:
                try:
                    address_token_to = desired_parsed_item_list[0][1][0]
                    address_value_to = desired_parsed_item_list[0][1][1]
                    token_amount = desired_parsed_item_list[1][1][0]
                    local_account = Account.privateKeyToAccount(desired_parsed_item_list[2][1][0])
                    safe_interface.command_send_token_raw(address_value_to, address_token_to, token_amount, local_account)
                except Exception as err:
                    print(type(err), err)

        elif command_argument == 'depositToken':
            if priority_group == 1:
                try:
                    address_value_to = desired_parsed_item_list[0][1][0]
                    token_amount = desired_parsed_item_list[1][1][0]
                    local_account = Account.privateKeyToAccount(desired_parsed_item_list[2][1][0])
                    safe_interface.command_deposit_token_raw(address_value_to, token_amount, local_account)
                except Exception as err:
                    print(type(err), err)
                    
        elif command_argument == 'withdrawToken':
            if priority_group == 1:
                try:
                    address_token_to = desired_parsed_item_list[0][1][0]
                    address_value_to = desired_parsed_item_list[0][1][1]
                    token_amount = desired_parsed_item_list[1][1][0]
                    safe_interface.command_withdraw_token_raw(address_value_to, address_token_to, token_amount)
                except Exception as err:
                    print(type(err), err)

        elif command_argument == 'sendEther':
            if priority_group == 1:
                try:
                    address_value_to = desired_parsed_item_list[0][1][0]
                    local_account = Account.privateKeyToAccount(desired_parsed_item_list[1][1][0])
                    ethereum_units_amount = desired_parsed_item_list[2:]
                    ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
                    amount_value = ether_helper.get_unify_ether_amount(ethereum_units_amount)
                    self.logger.debug0('Total Amount: {0} Wei'.format(amount_value))
                    safe_interface.command_send_ether_raw(address_value_to, amount_value, local_account)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'withdrawEther':
            if priority_group == 1:
                try:
                    address_value_to = desired_parsed_item_list[0][1][0]
                    ethereum_units_amount = desired_parsed_item_list[1:]
                    ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
                    amount_value = ether_helper.get_unify_ether_amount(ethereum_units_amount)
                    self.logger.debug0('Total Amount: {0} Wei'.format(amount_value))
                    safe_interface.command_withdraw_ether_raw(amount_value, address_value_to)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'depositEther':
            if priority_group == 1:
                try:
                    local_account = Account.privateKeyToAccount(desired_parsed_item_list[0][1][0])
                    ethereum_units_amount = desired_parsed_item_list[1:]
                    ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
                    amount_value = ether_helper.get_unify_ether_amount(ethereum_units_amount)
                    self.logger.debug0('Total Amount: {0} Wei'.format(amount_value))
                    safe_interface.command_deposit_ether_raw(amount_value, local_account)
                except Exception as err:
                    self.logger.error(err)

        elif command_argument == 'updateSafe':
            self.logger.info('updateSafe --address=0x to be Implemented')
            # note: Check Validity of The Safe Address & Version, Then Ask for Confirmation'

        elif command_argument == 'setDefaultSender':
            safe_interface.command_set_default_sender()

        elif command_argument == 'viewBalance':
            safe_interface.command_view_balance()
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

        elif command_argument == 'loadOwner':
            if priority_group == 1:
                private_key = desired_parsed_item_list[0][1][0]
                self.logger.debug0('[ Signature Value ]: {0} {1}'.format(str(private_key), safe_interface.safe_operator.retrieve_owners()))
                local_owner = self.account_artifacts.get_local_account(str(private_key), safe_interface.safe_operator.retrieve_owners())
                if local_owner in safe_interface.local_owner_account_list:
                    self.logger.error('Local Owner Already in local_owner_account_list')
                else:
                    safe_interface.local_owner_account_list.append(local_owner)
                    self.logger.debug0('[ Local Account Added ]: {0}'.format(safe_interface.local_owner_account_list))
                safe_interface.setup_sender()

        elif command_argument == 'unloadOwner':
            private_key = desired_parsed_item_list[0][1][0]
            self.logger.debug0('[ Signature Value ]: {0} {1}'.format(str(private_key), safe_interface.safe_operator.retrieve_owners()))
            local_owner = self.account_artifacts.get_local_account(private_key, safe_interface.safe_operator.retrieve_owners())

            if local_owner in safe_interface.local_owner_account_list:
                for local_owner_account in safe_interface.local_owner_account_list:
                    if local_owner_account == local_owner:
                        self.logger.debug0('REMOVING LOCAL ACCOUNT')
                        safe_interface.local_owner_account_list.remove(local_owner)

                safe_interface.setup_sender()
                self.logger.debug0('[ Local Account Subs ]: {0}'.format(safe_interface.local_owner_account_list))
            else:
                self.logger.error('Local Account generated via Private Key it is not Loaded')

        elif command_argument == 'loadMultipleOwners':
            self.logger.info('load multiple owners')
        elif command_argument == 'unloadMultipleOwners':
            self.logger.info('load multiple owners')

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
                    function_name, function_arguments, address_from, execute_flag, queue_flag, query_flag = \
                        self.console_getter.get_input_method_arguments(splitted_stream, contract_methods[item]['arguments'])
                    self.logger.debug0('command: {0} | arguments: {1} | execute_flag: {2} | query_flag: {3} | '.format(function_name, function_arguments, execute_flag, queue_flag))

                    if execute_flag or query_flag or queue_flag:
                        # remark: Transaction Solver
                        if execute_flag:
                            if contract_methods[item]['name'].startswith('get'):
                                self.logger.warn('transact() operation is discourage if you are using a getter method')
                            # if address_from != '':
                                # address_from = '\{\'from\':{0}\}'.format(address_from)

                            self.logger.info(contract_methods[item]['transact'].format(function_arguments, address_from))
                            resolution = eval(contract_methods[item]['transact'].format(function_arguments, address_from))
                            self.logger.info(resolution)
                            # this is the hash to be signed, maybe call for approve dialog, approveHash dialogue,
                            # map functions to be performed by the gnosis_py library

                        # remark: Call Solver
                        elif query_flag:
                            self.logger.info(contract_methods[item]['call'].format(function_arguments, address_from))
                            resolution = eval(contract_methods[item]['call'].format(function_arguments, address_from))
                            self.logger.info(resolution)
                        # remark: Add to the Batch Solver
                        elif queue_flag:
                            self.logger.info('(Future Implementation) executeBatch when you are ready to launch the transactions that you queued up!')
                    else:
                        self.logger.warn('--execute, --query or --queue arguments needed in order to properly operate with the current contract')

        except Exception as err:
            self.logger.debug0('operate_with_contract() {0}'.format(err))
