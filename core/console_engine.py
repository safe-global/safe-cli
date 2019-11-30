#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from core.contract.console_safe_commands import ConsoleSafeCommands
from core.contract.console_contract_commands import ConsoleContractCommands

from core.net.network_agent import NetworkAgent
from core.input.console_input_getter import ConsoleInputGetter

from core.contract.utils.console_syntax_lexer import ContractSyntaxLexer
from core.contract.utils.contract_method_completer import ContractMethodCompleter

from core.artifacts.console_contract_artifacts import ConsoleContractArtifacts
from core.artifacts.console_payload_artifacts import ConsolePayloadArtifacts
from core.artifacts.console_account_artifacts import ConsoleAccountsArtifacts
from core.console_controller import ConsoleController

# Import PromptToolkit Package
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import PromptSession

# Import Os Package
import os

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

# Constants
QUOTE = '\''
COMA = ','
PROJECT_DIRECTORY = os.getcwd() + '/assets/safe-contracts-1.1.0/'
STRING_DASHES = '----------' * 12

# style = Style.from_dict({
#     'completion-menu.completion': 'bg:#008888 #ffffff',
#     'completion-menu.completion.current': 'bg:#00aaaa #000000',
#     'scrollbar.background': 'bg:#88aaaa',
#     'scrollbar.button': 'bg:#222222',
# })

class GnosisConsoleEngine:
    def __init__(self, configuration):
        self.name = self.__class__.__name__
        self.pre_loaded_contract_artifacts = None
        self.prompt_text = './gnosis-cli'
        self.network = 'ganache'

        self.active_session = 'main'
        self.contract_methods = None
        self.contract_interface = None

        self.default_auto_fill = False
        self.session_config = {
            'prompt': self._get_prompt_text(stream=self.prompt_text),
            'contract_lexer': ContractSyntaxLexer(),
            'contract_completer': ContractMethodCompleter(),
            'gnosis_lexer': None,
            'style': 'Empty',
            'completer': WordCompleter(
                [
                    'about', 'info', 'help', 'newContract', 'loadContract', 'setNetwork', 'viewNetwork', 'viewTokens',
                    'close', 'quit', 'viewContracts', 'viewAccounts', 'newAccount', 'setAutofill', 'newToken'
                    'viewPayloads', 'newPayload', 'newTxPayload', 'setDefaultOwner', 'setDefaultOwnerList',
                    'viewOwners', 'dummyCommand', 'loadSafe'
                 ],
                ignore_case=True)
        }

        # Custom Logger Init Configuration: Default Values
        self.logging_lvl = INFO
        self.logger = None
        self._setup_console_init_configuration(configuration)

        # CustomLogger Format Definition: Output Init Configuration
        formatter = logging.Formatter(fmt='%(asctime)s - [%(levelname)s]: %(message)s', datefmt='%I:%M:%S - %p')

        # Custom Logger File Configuration: File Init Configuration
        file_handler = logging.FileHandler('./log/gnosis_console/general_console.log', 'w')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level=self.logging_lvl)

        # Custom Logger Console Configuration: Console Init Configuration
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level=self.logging_lvl)

        # Custom Logger Console/File Handler Configuration
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.safe_interface = None

        # Setup Contract Payloads
        self.payload_artifacts = ConsolePayloadArtifacts()
        # Setup Contract Artifacts
        self.contract_artifacts = ConsoleContractArtifacts()
        # Setup EthereumClient
        self.network_agent = NetworkAgent(self.logger)
        # Setup Console Input Getter
        self.console_getter = ConsoleInputGetter(self.logger)
        # Setup Console Account Artifacts
        self.account_artifacts = ConsoleAccountsArtifacts(
            self.logger, self.network_agent.get_ethereum_client(), self.silence_flag
        )
        self.console_controller = ConsoleController(
            self.logger, self.network_agent, self.account_artifacts,
            self.payload_artifacts, None, self.contract_artifacts, self
        )
        # Debug: Finished loading all the components of the gnosis-cli
        if not self.silence_flag:
            self.logger.info(STRING_DASHES)
            self.logger.info('| {0:^116} | '.format('Finished Gnosis Cli Setup'))
            self.logger.info(STRING_DASHES)

    def run_console_session(self, prompt_text):
        """ Run Console Session

        :param prompt_text:
        :param previous_session:
        :param contract_methods:
        :param contract_instance:
        :return:
        """
        if self.active_session == 'main':
            prompt_text = self.session_config['prompt']
        console_session = self.get_console_session()
        try:
            while True:
                try:
                    stream = console_session.prompt(prompt_text)
                    desired_parsed_item_list, priority_group, command_argument, argument_list = \
                        self.console_getter.get_gnosis_input_command_argument(stream)

                    if self.active_session == 'contract':
                        try:
                            self.console_controller.operate_with_contract(
                                stream, self.contract_methods, self.contract_interface
                            )
                        except Exception:
                            self.active_session = 'main'
                    elif self.active_session == 'safe':
                        try:
                            self.console_controller.operate_with_safe(
                                desired_parsed_item_list, priority_group,
                                command_argument, argument_list, self.safe_interface
                            )
                        except Exception:
                            self.active_session = 'main'
                    else:
                        self.console_controller.operate_with_console(
                            desired_parsed_item_list, priority_group, command_argument, argument_list
                        )

                    if (command_argument == 'close') or (command_argument == 'quit') or (command_argument == 'exit'):
                        self.active_session = 'main'
                        raise EOFError
                except KeyboardInterrupt:
                    continue  # remark: Control-C pressed. Try again.
                except EOFError:
                    break  # remark: Control-D pressed.
        except Exception as err:
            self.logger.error(err)

    def get_console_session(self):
        """ Get Console Session

        :param prompt_text:
        :param sub_console:
        :return:
        """
        if self.active_session != 'main':
            return PromptSession(completer=self.session_config['contract_completer'], lexer=self.session_config['contract_lexer'])
        return PromptSession(completer=self.session_config['completer'], lexer=self.session_config['contract_lexer'])

    def _setup_console_init_configuration(self, configuration):
        """ Setup Console Init Configuration
        This function will perform the necessary actions to setup the parameters provided in the initialization
        :param configuration:
        :return:
        """
        self.silence_flag = configuration['silence']
        self.network = configuration['network']
        if configuration['debug']:
            self.logging_lvl = DEBUG0

        # CustomLogger Instance Creation
        self.logger = CustomLogger(self.name, self.logging_lvl)

        # Call Account to add
        # if len(configuration['private_key']) > 0:
        #     for key_item in configuration['private_key']:
        #         self.console_accounts.add_account(key_item)

    def _setup_contract_artifacts(self, contract_artifacts):
        """ Load Contract Artifacts
        This function will load contract artifacts for the console to have access to
        :param contract_artifacts:
        :return:
        """
        self.pre_loaded_contract_artifacts = contract_artifacts
        # remark: Pre-Loading of the Contract Assets (Safe v1.1.0, Safe v1.0.0, Safe v-0.0.1)
        # remark: Map the Artifacts of the Assets
        # note: method 1, with alias
        self.contract_artifacts.add_artifact(contract_artifacts, alias=contract_artifacts['name'])
        # note: method 2, wihout alias
        for contract_artifacts_item in [contract_artifacts]:
            self.contract_artifacts.add_artifact(contract_artifacts_item)

    # note: Future command to it's own funciton
    def run_contract_console(self, desired_parsed_item_list, priority_group):
        """ Run Contract Console

        :param desired_parsed_item_list:
        :param priority_group:
        :return:
        """
        if priority_group == 0:
            tmp_alias = desired_parsed_item_list[0][1][0]
            self.logger.debug0('alias: {0}'.format(tmp_alias))
            try:
                # review: rename properly once the merge it is done
                self.contract_interface = self.contract_artifacts.get_value_from_alias(tmp_alias, 'instance')
                self.contract_methods = ConsoleContractCommands().map_contract_methods(self.contract_interface)
                self.active_session = 'contract'
                self.logger.info(STRING_DASHES)
                self.logger.info('| {0:^116} | '.format('Entering Contract Console'))
                self.logger.info(STRING_DASHES)
                self.run_console_session(prompt_text=self._get_prompt_text(affix_stream='./contract-cli', stream=tmp_alias))
            except KeyError as err:
                self.logger.error(err)

        elif priority_group == 1:
            self.logger.error(desired_parsed_item_list)

    def run_safe_console(self, desired_parsed_item_list, priority_group):
        """ Run Safe Console

        :param desired_parsed_item_list:
        :param priority_group:
        :return:
        """
        if priority_group == 0:
            self.logger.info('Do Nothing')

        elif priority_group == 1:
            tmp_address = desired_parsed_item_list[0][1][0]
            self.safe_interface = ConsoleSafeCommands(tmp_address, self.logger, self.account_artifacts, self.network_agent)
            self.active_session = 'safe'
            self.logger.info(STRING_DASHES)
            self.logger.info('| {0:^116} | '.format('Entering Safe Console'))
            self.logger.info(STRING_DASHES)
            self.run_console_session(prompt_text=self._get_prompt_text(affix_stream='./safe-cli', stream='Safe (' + tmp_address + ')'))

    def _get_prompt_text(self, affix_stream='', stream=''):
        """ Get Prompt Text

        :param contract_name:
        :return:
        """
        if affix_stream == '':
            return '[ {cli_name} ]>: '.format(cli_name=self.prompt_text)
        return '[ {affix_stream} ][ {stream} ]>: '.format(affix_stream=affix_stream, stream=stream)
