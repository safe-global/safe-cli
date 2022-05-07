# -*- coding: utf-8 -*-

# Import HTML for defining the prompt style
from prompt_toolkit import HTML
# Import Completer Module for the prompt
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
# Import Completer Constants defining the information of the commands withing the prompt

from contract_operator import METHOD_METHOD_META, METHOD_METHOD_TYPE_META


class ContractCompleter(Completer):
    """ Command Completer
    This class will perform the utilities regarding auto-completion of known user input commands
    """
    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Completion:
        """ Get Completions
        This will function will provide the completions for param types and function name
        :param document:
        :param complete_event:
        :return:
        """
        word = document.get_word_before_cursor()
        if document.find_previous_word_ending() is None:
            for _command in METHOD_METHOD_META:
                # note: force lower() to function as ignore_case.
                if _command.lower().startswith(word.lower()):
                    yield Completion(_command, start_position=-len(word), display=METHOD_METHOD_TYPE_META.get(_command),
                                     display_meta=METHOD_METHOD_META.get(_command))
