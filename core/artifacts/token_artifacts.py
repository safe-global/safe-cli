#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Enum Package
from enum import Enum

# Constant
STRING_DASHES = '---------' * 10


class TypeOfTokens(Enum):
    """ Type Of Tokens

    """
    ERC20 = 'ERC20'
    ERC721 = 'ERC721'


class TokenArtifacts:
    """ Token Artifacts

    """
    def __init__(self, logger):
        self.logger = logger
        self.token_data = {}

    def command_view_tokens(self):
        self.logger.debug0(STRING_DASHES)
        for item in self.token_data:
            self.logger.info(' | {0:^15} | {1:^25} | {2:^25} | {3:^25} | '.format(
                item, self.token_data[item]['address'], self.token_data[item]['instance'], self.token_data['type'])
            )
        self.logger.debug0(STRING_DASHES)

    def new_token_entry(self, token_addres, token_instance, type_of_tokens, alias):
        """

        :param token_addres:
        :param token_instance:
        :param type_of_tokens:
        :return:
        """
        return {
            'address': token_addres, 'instance': token_instance, 'token_type': type_of_tokens, 'name': alias
        }

    def add_token_artifact(self, token_artifact, alias='', type_of_token=TypeOfTokens.ERC20):
        """

        :param token_artifact:
        :param alias:
        :param type_of_token:
        :return:
        """
        if alias != '':
            self.token_data[alias] = self.new_token_entry(token_artifact['address'], token_artifact['instance'], type_of_token, alias)
        self.token_data['uToken' + str(len(self.token_data))] = self.new_token_entry(token_artifact['instance'], token_artifact['instance'], type_of_token, 'uToken' + str(len(self.token_data)))