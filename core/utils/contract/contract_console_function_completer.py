#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prompt_toolkit.completion import Completer, Completion
from core.utils.contract.contract_console_constants import *


class ContractFunctionCompleter(Completer):
    def get_completions(self, document, complete_event):
        """ Get Completions
        This will function will provide the completions for param types and function name
        :param document:
        :param complete_event:
        :return:
        """
        # for each word the completer gets
        previous_word = document.find_previous_word_ending()
        word = document.get_word_before_cursor()
        # if current word starts with -- eval argument if
        if previous_word is not None:
            for keyword in arg_keywords:
                if word in keyword:
                    yield Completion(keyword, start_position=-len(word), display=keyword)

        elif previous_word is None:
            for _function in function_name:
                if _function.startswith(word):
                    if _function in function_params:
                        family = function_params[_function]
                        family_color = function_parms_color.get(family, 'default')
                        display = HTML('%s<b>:</b> <ansired>(<' + family_color + '>%s</' + family_color + '>)</ansired>') % (_function, family)
                        yield Completion(_function, start_position=-len(word), display=display,
                                         display_meta=meta.get(_function))
                elif word == 'all':
                    yield Completion(_function, start_position=-len(word), display=_function, display_meta=meta.get(_function))
