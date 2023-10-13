import unittest

from pygments.token import Token

from safe_cli.safe_lexer import SafeLexer


class TestSafeLexer(unittest.TestCase):
    def test_get_tokens_unprocessed(self):
        safe_lexer = SafeLexer()

        self.assertEqual(
            next(safe_lexer.get_tokens_unprocessed("refresh")),
            (0, Token.Name.Builtin, "refresh"),
        )
        self.assertEqual(
            next(safe_lexer.get_tokens_unprocessed("not-supported-command")),
            (0, Token.Text, "not-supported-command"),
        )


if __name__ == "__main__":
    unittest.main()
