#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Console Commands Module
from core.contract.safe_commands import ConsoleSafeCommands
from core.contract.contract_commands import ConsoleContractCommands

# Import Handlers of the Console
from core.console_controller import ConsoleController
from core.input.console_input_getter import ConsoleInputGetter
from core.net.network_agent import NetworkAgent

# Import HTML for defining the prompt style
from prompt_toolkit import HTML
from prompt_toolkit.shortcuts import set_title

# Import Completer & SyntaxLexer
from core.contract.utils.syntax_lexer import SyntaxLexer
from core.contract.utils.command_completer import CommandCompleter

# Import Console Artifacts
from core.artifacts.data_artifacts import DataArtifacts
from core.artifacts.contract_artifacts import ContractArtifacts
from core.artifacts.payload_artifacts import PayloadArtifacts
from core.artifacts.account_artifacts import AccountsArtifacts
from core.artifacts.token_artifacts import TokenArtifacts
from core.artifacts.help_artifacts import InformationArtifacts

# Import PromptToolkit Package
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import yes_no_dialog

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

# Import TypeOfConsole Enum
from core.constants.console_constant import TypeOfConsole

# Import LogFileManager & LogMessageFormatter
from core.logger.log_file_manager import LogFileManager
from core.logger.log_message_formatter import LogMessageFormatter
from core.constants.console_constant import gnosis_commands

# Import EtherHelper for unifying ether amount quantities
from core.artifacts.utils.ether_helper import EtherHelper


class GnosisConsoleEngine:
    """ Gnosis Console Engine
    This class will perform the core activities for the console, launch the general purpose console, and the give
    access to the safe console via loadSafe --address=0x0*40 & access to the general contract console via
    loadContract --alias=GnosisSafeV1.1.0_1
    """
    def __init__(self, init_configuration):
        self.name = self.__class__.__name__
        self.prompt_text = init_configuration['name']
        # Setup the console files logs if does not exists
        LogFileManager().create_log_files()

        # Setup active console, default it's gnosis-cli
        self.active_session = TypeOfConsole.GNOSIS_CONSOLE

        # References to the methods for the sub consoles
        self.safe_interface = None
        self.contract_methods = None
        self.contract_interface = None

        self.session_config = {
            'prompt': self._get_prompt_text(affix_stream=self.prompt_text),
            'contract_lexer': SyntaxLexer(),
            'contract_completer': CommandCompleter(),
            'gnosis_lexer': None,
            'style': None,
            'completer': WordCompleter(gnosis_commands, ignore_case=True)
        }

        # Custom Logger Init Configuration: Default Values
        self.logging_lvl = INFO
        self.logger = None

        # Use Launch Configuration
        self._setup_console_logger_init(init_configuration)

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

        # Setup EthereumClient
        self.network_agent = NetworkAgent(self.logger, init_configuration['network'], init_configuration['api_key'])

        # Load Artifacts: Gnosis Console
        self.console_information = InformationArtifacts(self.logger)
        self.console_information.command_view_disclaimer()
        # Setup Contract Payloads
        self.payload_artifacts = PayloadArtifacts(self.logger)
        # Setup Contract Artifacts
        self.contract_artifacts = ContractArtifacts(self.logger)

        # Setup Console Input Getter
        self.console_getter = ConsoleInputGetter(self.logger)
        # Setup Console Account Artifacts
        self.account_artifacts = AccountsArtifacts(
            self.logger, self.network_agent.get_ethereum_client(), self.quiet_flag, self.test_flag
        )
        # Setup Console Token
        self.token_artifacts = TokenArtifacts(self.logger, self.network_agent.ethereum_client)

        # Setup DataArtifacts
        self.data_artifacts = DataArtifacts(
            self.logger, self.account_artifacts, self.payload_artifacts,
            self.token_artifacts, self.contract_artifacts
        )
        # Pass DataArtifacts to Controller
        self.console_controller = ConsoleController(self.logger, self.network_agent, self.data_artifacts, self)

        # Load Ether Helper for the bottom toolbar
        self.ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)

        # Setup: Log Formatter
        self.log_formatter = LogMessageFormatter(self.logger)

        self._setup_console_token_init(init_configuration)

        # Run Console
        self._setup_console_init(init_configuration)

    def exit_command(self, command_argument, argument_list):
        _, _, _now = self.console_getter.get_input_affix_arguments(argument_list)
        if (command_argument == 'close') or (command_argument == 'quit') or (command_argument == 'exit'):
            if not _now:
                if (self.active_session == TypeOfConsole.SAFE_CONSOLE) \
                        or (self.active_session == TypeOfConsole.CONTRACT_CONSOLE):
                    result = yes_no_dialog(
                        title='Exiting {0}'.format(self.active_session.value),
                        text='All data regarding loaded owners & sender configuration will be lost, '
                             'Are you sure you want to exit the {0}?'.format(self.active_session.value)).run()
                else:
                    result = yes_no_dialog(
                        title='Exiting {0}'.format(self.active_session.value),
                        text='All data regarding accounts, tokens, contracts & payloads will be lost, '
                             'Are you sure you want to exit the {0}?'.format(self.active_session.value)).run()
                if result:
                    self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                    raise EOFError

            elif _now:
                self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                raise EOFError

    def run_console_session(self, prompt_text):
        """ Run Console Session
        This function will launch the gnosis cli
        :param prompt_text:
        :return:
        """
        if self.active_session == TypeOfConsole.GNOSIS_CONSOLE:
            set_title('Gnosis Console')
            prompt_text = self.session_config['prompt']
        console_session = self.get_console_session()
        try:
            while True:
                try:
                    if self.active_session == TypeOfConsole.SAFE_CONSOLE:
                        stream = console_session.prompt(
                            prompt_text,
                            bottom_toolbar=self.get_toolbar_text(
                                self.safe_interface.sender_address,
                                self.safe_interface.sender_private_key),
                            refresh_interval=0.5)
                    else:
                        stream = console_session.prompt(prompt_text)
                    desired_parsed_item_list, priority_group, command_argument, argument_list = \
                        self.console_getter.get_gnosis_input_command_argument(stream)
                    if self.active_session == TypeOfConsole.CONTRACT_CONSOLE:
                        try:
                            self.console_controller.operate_with_contract(
                                stream, self.contract_methods, self.contract_interface)
                        except Exception:
                            self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                    elif self.active_session == TypeOfConsole.SAFE_CONSOLE:
                        try:
                            self.console_controller.operate_with_safe(
                                desired_parsed_item_list, priority_group,
                                command_argument, argument_list, self.safe_interface)
                        except Exception:
                            self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                    else:
                        try:
                            self.console_controller.operate_with_console(
                                desired_parsed_item_list, priority_group, command_argument, argument_list)
                        except Exception as err:
                            self.logger.error('Something Went Wrong Opss {0}  {1}'.format(type(err), err))
                            self.active_session = TypeOfConsole.GNOSIS_CONSOLE

                    self.exit_command(command_argument, argument_list)
                except KeyboardInterrupt:
                    # remark: Control-C pressed. Try again.
                    continue
                except EOFError:
                    # remark: Control-D pressed.
                    break
        except Exception as err:
            self.logger.error(err)

    def get_console_session(self):
        """ Get Console Session
        Get Console Session based on the self.active_session =
        :return:
        """
        if self.active_session is not TypeOfConsole.GNOSIS_CONSOLE:
            return PromptSession(
                completer=self.session_config['contract_completer'],
                lexer=self.session_config['contract_lexer'])
        return PromptSession(
            completer=self.session_config['completer'],
            lexer=self.session_config['contract_lexer'])

    def _setup_console_logger_init(self, configuration):
        """ Setup Console Init Configuration
        This function will perform the necessary actions to setup the parameters provided in the initialization
        :param configuration:
        :return:
        """
        self.quiet_flag = configuration['quiet']
        self.test_flag = configuration['test']
        if configuration['debug']:
            self.logging_lvl = DEBUG0

        # CustomLogger Instance Creation
        self.logger = CustomLogger(self.name, self.logging_lvl)

    def _setup_console_token_init(self, configuration):
        """ Setup Console Token Configuration

        :param configuration:
        :return:
        """
        if configuration['erc20']:
            self.logger.debug0(configuration['erc20'])
            self.token_artifacts.pre_load_erc20_artifacts(configuration['erc20'])

        if configuration['erc721']:
            self.logger.debug0(configuration['erc721'])
            self.token_artifacts.pre_load_erc20_artifacts(configuration['erc721'])

    def _setup_console_init(self, configuration):
        """ Setup Console Safe Configuration

        :param configuration:
        :return:
        """
        if configuration['safe'] is not None:
            if self.network_agent.ethereum_client.w3.isAddress(configuration['safe']):
                try:
                    self.log_formatter.log_entry_message('Entering Safe Console')
                    set_title('Safe Console')
                    self.logger.debug0(configuration['safe'])
                    self.run_safe_console(configuration['safe'], configuration['private_key'])
                except Exception as err:
                    self.logger.err('{0}'.format(self.name))
                    self.logger.err(err)
        else:
            # Info Header: Finished loading all the components of the gnosis-cli
            if not self.quiet_flag:
                self.log_formatter.log_entry_message('Entering Gnosis Cli')
            self.run_console_session(self.prompt_text)

    def _setup_console_contract_configuration(self, configuration):
        """ Setup Console Contract Configuration
        This function will load contract artifacts for the console to have access to
        :param configuration:
        :return:
        """

        if configuration['contract'] and configuration['abi']:
            self.logger.debug0(configuration['contract'])
            self.logger.debug0(configuration['abi'])
            self.logger.info('This should load the contract information')

        # if contract_artifacts is not None:
        #     # remark: Pre-Loading of the Contract Assets (Safe v1.1.0, Safe v1.0.0, Safe v-0.0.1)
        #     #  for testing purposes
        #     for artifact_index, artifact_item in enumerate(contract_artifacts):
        #         self.contract_artifacts.add_contract_artifact(
        #             artifact_item['name'], artifact_item['instance'],
        #             artifact_item['abi'], artifact_item['bytecode'],
        #             artifact_item['address'], alias=contract_artifacts['name'])

    def run_contract_console(self, contract_alias):
        """ Run Contract Console
        This function will run the contract console
        :param contract_alias:
        :return:
        """
        try:
            self.log_formatter.log_entry_message('Entering Contract Console')
            set_title('Contract Console')
            self.contract_interface = self.contract_artifacts.retrive_from_stored_values(contract_alias, 'instance')
            self.logger.debug0('Contract Instance {0} Loaded'.format(self.contract_interface))
            self.contract_methods = ConsoleContractCommands().map_contract_methods(self.contract_interface)
            self.active_session = TypeOfConsole.CONTRACT_CONSOLE
            self.run_console_session(prompt_text=self._get_prompt_text(affix_stream='contract-cli', stream=contract_alias))
        except KeyError as err:
            self.logger.error(err)

    def run_safe_console(self, safe_address, private_key_list=None):
        """ Run Safe Console
        This function will run the safe console
        :param safe_address:
        :param private_key_list:
        :return:
        """
        try:

            self.safe_interface = ConsoleSafeCommands(safe_address, self.logger, self.data_artifacts, self.network_agent)
            if private_key_list is not None:
                self.logger.debug0(private_key_list)
                for private_key_owner in private_key_list:
                    self.safe_interface.command_load_owner(private_key_owner)
            self.active_session = TypeOfConsole.SAFE_CONSOLE
            self.run_console_session(
                prompt_text=self._get_prompt_text(affix_stream='safe-cli', stream='Safe (' + safe_address + ')'))
        except KeyError as err:
            self.logger.error(err)

    def get_toolbar_text(self, sender_address=None, sender_private_key=None):
        amount = 0
        if (sender_address is not None) and (sender_private_key is not None):
            balance = self.network_agent.ethereum_client.w3.eth.getBalance(sender_address)
            wei_amount = self.ether_helper.get_unify_ether_amount([('--wei', [balance])])
            text_badge, tmp_amount = self.ether_helper.get_proper_ether_amount(wei_amount)
            amount = '{0} {1}'.format(str(tmp_amount), text_badge)
        return HTML((' [ <strong>Sender:</strong> %s | <strong>PK:</strong> %s | <strong>Balance:</strong> %s ]') % (sender_address, sender_private_key, amount))

    def _get_prompt_text(self, affix_stream='', stream=''):
        """ Get Prompt Text
        This function will generate the string that will be shown as the prompt text
        :param affix_stream:
        :param stream:
        :return:
        """
        return HTML(('<ansiblue>[ </ansiblue><strong>./%s</strong><ansiblue> ][ </ansiblue><strong>%s</strong><ansiblue> ]: </ansiblue>') % (affix_stream, stream))
