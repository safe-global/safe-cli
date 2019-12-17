#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Contract Reader Module
from core.eth_assets.helper.contract_reader import ContractReader

# Import Console Commands Module
from core.modules.safe_cli import ConsoleSafeCommands
from core.modules.contract_cli.contract_commands import ConsoleContractCommands

# Import Handlers of the Console
from core.modules.gnosis_cli.gnosis_controller import ConsoleController
from core.input.console_input_getter import ConsoleInputGetter
from core.net.network_agent import NetworkAgent

# Import HTML for defining the prompt style
from prompt_toolkit import HTML
from prompt_toolkit.shortcuts import set_title

# Import Completer & SyntaxLexer
from core.modules.contract_cli import SyntaxLexer
from core.modules.contract_cli import CommandCompleter

# Import Console Artifacts
from core.eth_assets.assets_engine import AssetsEngine
from core.eth_assets.contracts import ContractArtifacts
from core.eth_assets.payloads import Payloads
from core.eth_assets.accounts import Accounts
from core.eth_assets.tokens import Tokens
from core.eth_assets.help_artifacts import InformationArtifacts

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
from core.eth_assets.helper.ether_helper import EtherHelper


class GnosisConsoleEngine:
    """ Gnosis Console Engine
    This class will perform the core activities for the console, launch the general purpose console, and the give
    access to the safe console via loadSafe --address=0x0*40 & access to the general contract_cli console via
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

        # Setup Contract ABI Reader
        self.contract_reader = ContractReader(self.logger)

        # Setup EthereumClient
        self.network_agent = NetworkAgent(self.logger, init_configuration['network'], init_configuration['api_key'])

        # Load Artifacts: Gnosis Console
        self.console_information = InformationArtifacts(self.logger)
        self.console_information.command_view_disclaimer()
        # Setup Contract Payloads
        self.payload_artifacts = Payloads(self.logger)
        # Setup Contract Artifacts
        self.contract_artifacts = ContractArtifacts(self.logger)

        # Setup Console Input Getter
        self.console_getter = ConsoleInputGetter(self.logger)
        # Setup Console Account Artifacts
        self.account_artifacts = Accounts(
            self.logger, self.network_agent.get_ethereum_client(), self.quiet_flag, self.test_flag
        )
        # Setup Console Token
        self.token_artifacts = Tokens(self.logger, self.network_agent.ethereum_client)

        # Setup DataArtifacts
        self.data_artifacts = AssetsEngine(
            self.logger, self.account_artifacts, self.payload_artifacts,
            self.token_artifacts, self.contract_artifacts
        )
        # Pass DataArtifacts to Controller
        self.console_controller = ConsoleController(self.logger, self.network_agent, self.data_artifacts, self)

        # Load Ether Helper for the bottom toolbar
        self.ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)

        # Setup: Log Formatter
        self.log_formatter = LogMessageFormatter(self.logger)

        # Setup Token & Contract Artifacts
        # self._setup_console_token_init(init_configuration)
        # self._setup_console_contract_configuration(init_configuration)

        # Run Console
        self._setup_console_init(init_configuration)

    def exit_command(self, command_argument, argument_list):
        _, _, _, _now = self.console_getter.get_input_affix_arguments(argument_list)
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

    def run(self):
        """ Run Console Session
        This function will launch the gnosis cli
        :return:
        """
        prompt_text = self.session_config['prompt']
        console_session = self.get_gnosis_console()
        try:
            while True:
                try:
                    if self.active_session == TypeOfConsole.SAFE_CONSOLE:
                        self.console_controller.operate_with_safe(
                            desired_parsed_item_list,
                            priority_group,
                            command_argument,
                            argument_list,
                            self.safe_interface)

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

    def get_gnosis_console(self):
        """ Get Console Session
        Get Console Session based on the self.active_session =
        :return:
        """
        return PromptSession(completer=self.session_config['completer'], lexer=self.session_config['contract_lexer'])

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

    def _setup_console_init(self, configuration):
        """ Setup Console Safe Configuration

        :param configuration:
        :return:
        """
        if not self.quiet_flag:
            self.log_formatter.log_entry_message('Entering Gnosis Cli')
        self.run(self.prompt_text)

    def _get_prompt_text(self, affix_stream='', stream=''):
        """ Get Prompt Text
        This function will generate the string that will be shown as the prompt text
        :param affix_stream:
        :param stream:
        :return:
        """
        return HTML('<ansiblue>[ </ansiblue><strong>./%s</strong><ansiblue> ]'
                    '[ </ansiblue><strong>%s</strong><ansiblue> ]: </ansiblue>' % (affix_stream, stream))
