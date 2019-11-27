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


class ContractLexer(Lexer):
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

        :param document:
        :return:
        """
        # remark: Color Palette
        # Todo: Make a proper Color Scheme for the params and function_names
        colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))

        def get_line(lineno):
            aux_list = []
            for index, word in enumerate(document.lines[lineno].split(' ')):
                current_color = colors[10 % len(colors)]
                if self.__is_valid_argument(simple_function_name, word):
                    current_color = colors[50 % len(colors)]
                elif self.__is_valid_argument(normal_address, word):
                    current_color = colors[250 % len(colors)]
                elif self.__is_valid_argument(uint_data, word):
                    current_color = colors[110 % len(colors)]
                elif self.__is_valid_argument(bytecode_data, word):
                    current_color = colors[140 % len(colors)]
                elif self.__is_valid_argument(execute, word):
                    current_color = colors[170 % len(colors)]
                elif self.__is_valid_argument(queue, word):
                    current_color = colors[200 % len(colors)]
                elif self.__is_valid_argument(_exit, word):
                    current_color = colors[230 % len(colors)]
                aux_list.append((current_color, word + ' '))
            return aux_list
        return get_line