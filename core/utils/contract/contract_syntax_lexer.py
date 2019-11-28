#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Import Prompt Tool Packages
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS

# Import Regex Expresions from Contract Console Constants Package
from core.utils.contract.contract_console_constants import (
    _exit, simple_function_name, normal_address, uint_data, execute, queue, bytecode_data
)

# Import Re Package
import re
BASIC_TEXT = 'LightGray'
BASE_HIGHLIGHT_COLOR = 'MidnightBlue'
PARAM_COLOR = 'SlateBlue'
EXIT_COLOR = 'Tomato'
CONTRACT_METHODS_COLOR = 'DarkOrange'
CONSOLE_COMMANDS = 'SaddleBrown'
CONTRACT_EXEC_CALL_QUEUE = 'DarkSalmon'

class ContractSyntaxLexer(Lexer):
    """ Contract Lexer

    """
    @staticmethod
    def __is_valid_argument(regular_expresion, stream):
        """ Is Valid Argument
        This function will try to retrieve a piece of input stream, if group(0) does not raise AttributeError it will
        return True, otherwise False

        :param regular_expresion:
        :param stream:
        :return:
        """
        try:
            re.search(regular_expresion, stream).group(0)
            return True
        except AttributeError:
            return False

    def lex_document(self, document):
        """ Lex Document
        This function will change the color of the document text to fit the proper syntax highlight
        :param document: stream input provided by the console user
        :return: output colored syntax
        """
        # remark: Color Palette
        # Todo: Make a proper Color Scheme for the params and function_names
        colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))

        def get_line(lineno):
            aux_list = []
            for index, word in enumerate(document.lines[lineno].split(' ')):
                current_color = BASIC_TEXT
                if self.__is_valid_argument(simple_function_name, word):
                    current_color = CONTRACT_METHODS_COLOR
                elif self.__is_valid_argument(normal_address, word) or self.__is_valid_argument(uint_data, word) or self.__is_valid_argument(bytecode_data, word):
                    current_color = PARAM_COLOR
                elif self.__is_valid_argument(queue, word) or self.__is_valid_argument(execute, word):
                    current_color = CONSOLE_COMMANDS
                elif self.__is_valid_argument(_exit, word) or self.__is_valid_argument('close', word) or self.__is_valid_argument('quit', word):
                    current_color = EXIT_COLOR
                aux_list.append((current_color, word + ' '))
            return aux_list
        return get_line