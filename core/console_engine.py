#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# review: Decouple This!
# Import ConsoleSafeCommands
from core.contract.safe_commands import ConsoleSafeCommands
from core.contract.contract_commands import ConsoleContractCommands

from core.net.network_agent import NetworkAgent
from core.console_controller import ConsoleController
from core.input.console_input_getter import ConsoleInputGetter

from core.contract.utils.syntax_lexer import SyntaxLexer
from core.contract.utils.command_completer import CommandCompleter

from core.artifacts.contract_artifacts import ContractArtifacts
from core.artifacts.payload_artifacts import PayloadArtifacts
from core.artifacts.account_artifacts import AccountsArtifacts

# Import PromptToolkit Package
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import PromptSession

# Import Os Package
import os

# Import Enum Package
from enum import Enum

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

from core.artifacts.data_artifacts import DataArtifacts

# Constants
QUOTE = '\''
COMA = ','
PROJECT_DIRECTORY = os.getcwd() + '/assets/safe-contracts-1.1.0/'
STRING_DASHES = '----------' * 12


# Todo: use values to define state of the console
class TypeOfConsole(Enum):
    GNOSIS_CONSOLE = 'gnosis-cli'
    CONTRACT_CONSOLE = 'contract-cli'
    SAFE_CONSOLE = 'safe-cli'


class GnosisConsoleEngine:
    def __init__(self, init_configuration, contract_artifacts=None):
        self.name = self.__class__.__name__
        self.prompt_text = init_configuration['name']

        # Setup active console, default it's gnosis-cli
        self.active_session = TypeOfConsole.GNOSIS_CONSOLE

        # References to the methods for the sub consoles
        self.safe_interface = None
        self.contract_methods = None
        self.contract_interface = None

        self.network = 'ganache'
        self.default_auto_fill = False

        self.session_config = {
            'prompt': self._get_prompt_text(affix_stream=self.prompt_text),
            'contract_lexer': SyntaxLexer(),
            'contract_completer': CommandCompleter(),
            'gnosis_lexer': None,
            'style': None,
            'completer': WordCompleter(
                [
                    'about', 'info', 'help', 'newContract', 'loadContract', 'setNetwork', 'viewNetwork', 'viewTokens',
                    'close', 'quit', 'viewContracts', 'viewAccounts', 'newAccount', 'setAutofill', 'newToken'
                    'viewPayloads', 'newPayload', 'newTxPayload', 'setDefaultSender', 'loadSafe', 'viewPayloads',
                    'dummyCommand'
                 ],
                ignore_case=True)
        }

        # Custom Logger Init Configuration: Default Values
        self.logging_lvl = INFO
        self.logger = None
        self._setup_console_init_configuration(init_configuration)

        # CustomLogger Format Definition: Output Init Configuration
        formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                                      datefmt='%I:%M:%S %p')
        detailed_formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                                               datefmt='%m/%d/%Y %I:%M:%S %p')

        # Custom Logger File Configuration: File Init Configuration
        file_handler = logging.FileHandler('./log/general_console.log', 'w')
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(level=self.logging_lvl)

        # Custom Logger Console Configuration: Console Init Configuration
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level=self.logging_lvl)

        # Custom Logger Console/File Handler Configuration
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Setup Contract Payloads
        self.payload_artifacts = PayloadArtifacts(self.logger)
        # Setup Contract Artifacts
        self.contract_artifacts = ContractArtifacts(self.logger)
        self.contract_artifacts.pre_load_artifacts(contract_artifacts)
        # Setup EthereumClient
        self.network_agent = NetworkAgent(self.logger)
        # Setup Console Input Getter
        self.console_getter = ConsoleInputGetter(self.logger)
        # Setup Console Account Artifacts
        self.account_artifacts = AccountsArtifacts(
            self.logger, self.network_agent.get_ethereum_client(), self.quiet_flag
        )

        # Setup DataArtifacts
        # self.data_artifacts = DataArtifacts()
        self.console_controller = ConsoleController(
            self.logger, self.network_agent, self.account_artifacts,
            self.payload_artifacts, None, self.contract_artifacts, self
        )
        # Debug: Finished loading all the components of the gnosis-cli
        if not self.quiet_flag:
            self.logger.info(STRING_DASHES)
            self.logger.info('| {0:^116} | '.format('Entering Gnosis Cli'))
            self.logger.info(STRING_DASHES)

        # Run Console
        self.run_console_session(self.prompt_text)

    def run_console_session(self, prompt_text):
        """ Run Console Session
        This function will launch the gnosis cli
        :param prompt_text:
        :param previous_session:
        :param contract_methods:
        :param contract_instance:
        :return:
        """

        if self.active_session == TypeOfConsole.GNOSIS_CONSOLE:
            prompt_text = self.session_config['prompt']
        console_session = self.get_console_session()
        try:
            while True:
                try:
                    stream = console_session.prompt(prompt_text)
                    desired_parsed_item_list, priority_group, command_argument, argument_list = \
                        self.console_getter.get_gnosis_input_command_argument(stream)

                    if self.active_session == TypeOfConsole.CONTRACT_CONSOLE:
                        try:
                            self.console_controller.operate_with_contract(
                                stream, self.contract_methods, self.contract_interface
                            )
                        except Exception:
                            self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                    elif self.active_session == TypeOfConsole.SAFE_CONSOLE:
                        try:
                            self.console_controller.operate_with_safe(
                                desired_parsed_item_list, priority_group,
                                command_argument, argument_list, self.safe_interface
                            )
                        except Exception:
                            self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                    else:
                        try:
                            self.console_controller.operate_with_console(
                                desired_parsed_item_list, priority_group, command_argument, argument_list
                            )
                        except Exception as err:
                            self.logger.error('Something Went Wrong Opss {0}  {1}'.format(type(err), err))
                            self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                    if (command_argument == 'close') or (command_argument == 'quit') or (command_argument == 'exit'):
                        self.active_session = TypeOfConsole.GNOSIS_CONSOLE
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
        if self.active_session is not TypeOfConsole.GNOSIS_CONSOLE:
            return PromptSession(completer=self.session_config['contract_completer'], lexer=self.session_config['contract_lexer'])
        return PromptSession(completer=self.session_config['completer'], lexer=self.session_config['contract_lexer'])

    def _setup_console_init_configuration(self, configuration):
        """ Setup Console Init Configuration
        This function will perform the necessary actions to setup the parameters provided in the initialization
        :param configuration:
        :return:
        """
        self.quiet_flag = configuration['quiet']
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
        """ Pre Load Contract Artifacts
        This function will load contract artifacts for the console to have access to
        :param contract_artifacts:
        :return:
        """
        if contract_artifacts is not None:
            # remark: Pre-Loading of the Contract Assets (Safe v1.1.0, Safe v1.0.0, Safe v-0.0.1) for testing purposes
            for artifact_index, artifact_item in enumerate(contract_artifacts):
                print(artifact_index)
                self.contract_artifacts.add_contract_artifact(
                    artifact_item['name'], artifact_item['instance'],
                    artifact_item['abi'], artifact_item['bytecode'],
                    artifact_item['address'], alias=contract_artifacts['name']
                )

    def run_contract_console(self, desired_parsed_item_list, priority_group):
        """ Run Contract Console
        This function will run the contract console
        :param desired_parsed_item_list:
        :param priority_group:
        :return:
        """
        if priority_group == 0:
            tmp_alias = desired_parsed_item_list[0][1][0]
            self.logger.debug0('alias: {0}'.format(tmp_alias))
            try:
                self.contract_interface = self.contract_artifacts.get_value_from_alias(tmp_alias, 'instance')
                self.logger.debug0('Contract Instance {0} Loaded'.format(self.contract_interface))
                self.contract_methods = ConsoleContractCommands().map_contract_methods(self.contract_interface)
                self.active_session = TypeOfConsole.CONTRACT_CONSOLE
                self.logger.info(STRING_DASHES)
                self.logger.info('| {0:^116} | '.format('Entering Contract Console'))
                self.logger.info(STRING_DASHES)
                self.run_console_session(prompt_text=self._get_prompt_text(affix_stream='contract-cli', stream=tmp_alias))
            except KeyError as err:
                self.logger.error(err)

        elif priority_group == 1:
            self.logger.error(desired_parsed_item_list)

    def run_safe_console(self, desired_parsed_item_list, priority_group):
        """ Run Safe Console
        This function will run the safe console
        :param desired_parsed_item_list:
        :param priority_group:
        :return:
        """
        if priority_group == 0:
            self.logger.info('Do Nothing')

        elif priority_group == 1:
            tmp_address = desired_parsed_item_list[0][1][0]
            self.safe_interface = ConsoleSafeCommands(tmp_address, self.logger, self.account_artifacts, self.network_agent)
            self.active_session = TypeOfConsole.SAFE_CONSOLE
            self.logger.info(STRING_DASHES)
            self.logger.info('| {0:^116} | '.format('Entering Safe Console'))
            self.logger.info(STRING_DASHES)
            self.run_console_session(prompt_text=self._get_prompt_text(affix_stream='safe-cli', stream='Safe (' + tmp_address + ')'))

    def _get_prompt_text(self, affix_stream='', stream=''):
        """ Get Prompt Text

        :param contract_name:
        :return:
        """
        return '[ ./{affix_stream} ][ {stream} ]>: '.format(affix_stream=affix_stream, stream=stream)
