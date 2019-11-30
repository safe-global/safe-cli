#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Enum Package
from enum import Enum

# Constant
STRING_DASHES = '---------' * 10


class TypeOfTokens(Enum):
    ERC20 = 'ERC20'
    ERC721 = 'ERC721'


class ConsoleTokenArtifacts:
    def __init__(self, logger):
        self.logger = logger
        self.token_data = {}

    def command_view_accounts(self):
        self.logger.debug0(STRING_DASHES)
        for item in self.token_data:
            self.logger.info(' | {0:^15} | {1:^25} | {2:^25} | {3:^25} | '.format(
                item, self.token_data[item]['address'], self.token_data[item]['instance'],
                self.token_data['token_type'])
            )
        self.logger.debug0(STRING_DASHES)

    def new_token_entry(self, token_addres, token_instance, type_of_tokens):
        """

        :param token_addres:
        :param token_instance:
        :param type_of_tokens:
        :return:
        """
        return {
            'address': token_addres, 'instance': token_instance, 'token_type': type_of_tokens
        }

    def add_token(self, token_artifact, alias='', type_of_token=TypeOfTokens.ERC20):
        """

        :param token_artifact:
        :param alias:
        :param type_of_token:
        :return:
        """
        if alias != '':
            self.token_data[alias] = self.new_token_entry(token_artifact['instance'], token_artifact['instance'], type_of_token)
            return self.token_data
        self.token_data['uToken' + str(len(self.token_data))] = self.new_token_entry(token_artifact['instance'], token_artifact['instance'], type_of_token)
        return self.token_data

    def get_payload_from_alias(self, alias, key=None):
        """

        :param alias:
        :param key:
        :return:
        """
        try:
            if key is None:
                return self.token_data[alias]
            return self.token_data[alias]['instance']
        except KeyError:
            raise KeyError
        except Exception as err:
            print(type(err), err)