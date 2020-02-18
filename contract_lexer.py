# -*- coding: utf-8 -*-

import re

from pygments.lexers.shell import BashLexer
from pygments.token import Keyword, Name, Text, Token


class ContractLexer(BashLexer):
    name = 'ContractLexer'
    aliases = ['contract_lexer']

    ADDRESS = r'^0x[aA-zZ,0-9]{40}$|^0x[aA-zZ,0-9]{62}$'
    EXTRA_KEYWORDS = {'info', 'refresh'}
    contract_keywords = set()

    def get_tokens_unprocessed(self, text: str) -> (int, Token, str):
        for index, token, value in BashLexer.get_tokens_unprocessed(self, text):
            if token is Text and value in self.EXTRA_KEYWORDS:
                yield index, Name.Builtin, value
            if token is Text and value in self.contract_keywords:
                yield index, Name.Builtin, value
            elif token is Text and re.search(self.ADDRESS, value):
                yield index, Keyword, value
            else:
                yield index, token, value
