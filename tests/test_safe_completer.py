import unittest

from prompt_toolkit.completion import CompleteEvent, Completion
from prompt_toolkit.document import Document

from safe_cli.safe_completer import SafeCompleter


class TestSafeCompleter(unittest.TestCase):
    def test_get_completions(self):
        safe_completer = SafeCompleter()

        with self.assertRaises(StopIteration):
            next(
                safe_completer.get_completions(
                    Document("not-supported-command"), CompleteEvent()
                )
            )

        self.assertIsInstance(
            next(
                safe_completer.get_completions(Document("send_ether"), CompleteEvent())
            ),
            Completion,
        )


if __name__ == "__main__":
    unittest.main()
