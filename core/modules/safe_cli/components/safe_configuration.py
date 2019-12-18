#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Completer & SyntaxLexer
from core.modules.safe_cli.prompt_components.safe_lexer import SafeLexer
from core.modules.safe_cli.prompt_components.safe_completer import SafeCompleter

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Constants
ON = 'ON'
OFF = 'OFF'


class SafeConfiguration:
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

        # Formatter: view functions
        self.log_formatter = LogMessageFormatter(self.logger)

        # Configuration variable
        self.auto_execute = False
        self.auto_fill_token_decimals = False

    def view_auto_execute(self):
        self.log_formatter.log_section_left_side('setAutoExecute')
        self.log_formatter.log_data(' (#) setAutoExecute set to {0}', self.auto_execute)
        self.log_formatter.log_dash_splitter()

    def set_auto_execute(self, value):
        if (value == ON) or (value == ON.lower()):
            self.auto_execute = True
        elif (value == OFF) or (value == OFF.lower()):
            self.auto_execute = False

        # Preview status for auto_execute
        self.view_auto_execute()

    def view_auto_fill_token_decimals(self):
        self.log_formatter.log_section_left_side('setAutoFillTokenDecimals')
        self.log_formatter.log_data(' (#) setAutoFillTokenDecimals set to {0}', self.auto_fill_token_decimals)
        self.log_formatter.log_dash_splitter()

    def command_set_auto_fill_token_decimals(self, value):
        if (value == ON) or (value == ON.lower()):
            self.auto_fill_token_decimals = True
        elif (value == OFF) or (value == OFF.lower()):
            self.auto_fill_token_decimals = False

        # Preview status for auto_fill_token_decimals
        self.view_auto_fill_token_decimals()

