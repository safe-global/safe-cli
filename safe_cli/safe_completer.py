from prompt_toolkit import HTML
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from .safe_completer_constants import (
    meta,
    safe_color_arguments,
    safe_commands,
    safe_commands_arguments,
)


class SafeCompleter(Completer):
    """
    This class will handle auto-completion of known user input commands
    """

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Completion:
        """
        Provide command completion for function names and param types

        :param document:
        :param complete_event:
        :return:
        """
        word = document.get_word_before_cursor()
        if document.find_previous_word_ending() is None:
            for command in safe_commands:
                # note: force lower() to function as ignore_case.
                if command.startswith(word.lower()):
                    if command in safe_commands_arguments:
                        safe_command = safe_commands_arguments[command]
                        safe_argument_color = safe_color_arguments.get(
                            safe_command, "default"
                        )
                        display = HTML(
                            "<b><ansired> &gt; </ansired>%s</b> <"
                            + safe_argument_color
                            + ">%s</"
                            + safe_argument_color
                            + ">"
                        ) % (command, safe_command)
                        yield Completion(
                            command,
                            start_position=-len(word),
                            display=display,
                            display_meta=meta.get(command),
                        )
