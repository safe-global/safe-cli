#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Constants & Common Enum TypeOfTokens Modules
from core.constants.console_constant import STRING_DASHES
from core.constants.enum_types import TypeOfTokens


class TokenArtifacts:
    """ Token Artifacts
    This class will store the token_artifacts for the console
    """
    def __init__(self, logger):
        self.logger = logger
        self.token_data = {}

    def command_view_tokens(self):
        """ Command View Tokens
        This function will show the current token_data, trigger via user input command "viewTokens"
        :return:
        """
        self.logger.debug0(STRING_DASHES)
        for item in self.token_data:
            self.logger.info(' | {0:^15} | {1:^25} | {2:^25} | {3:^25} | '.format(
                item, self.token_data[item]['address'], self.token_data[item]['instance'], self.token_data['type'])
            )
        self.logger.debug0(STRING_DASHES)

    def new_token_entry(self, token_addres, token_instance, type_of_tokens, alias):
        """ New Token Entry
        This function will generate a new entry dict for the token_data
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
        This function will add a new token_artifact to the token_data dict
        :param token_artifact:
        :param alias:
        :param type_of_token:
        :return:
        """
        if alias != '':
            self.token_data[alias] = self.new_token_entry(token_artifact['address'], token_artifact['instance'], type_of_token, alias)
        self.token_data['uToken' + str(len(self.token_data))] = self.new_token_entry(token_artifact['instance'], token_artifact['instance'], type_of_token, 'uToken' + str(len(self.token_data)))