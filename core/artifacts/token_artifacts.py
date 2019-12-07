#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Constants & Common Enum TypeOfTokens Modules
from core.constants.console_constant import STRING_DASHES
from core.artifacts.constants.type_artifacts import TypeOfTokens


class TokenArtifacts:
    """ Token Artifacts
    This class will store the token_artifacts for the console
    """
    def __init__(self, logger):
        self.logger = logger
        self.token_data = {}

    def pre_loaded_token_artifacts(self, token_artifacts):
        """ Pre Load Artifacts
        This function will pre-load any provided contract artifact, during the launching process of the general console
        gnosis-cli.
        :param token_artifacts:
        :return:
        """
        if token_artifacts is not None:
            self.logger.debug0('')
            self.logger.debug0(' | Setup Token Artifacts  | ')
            self.logger.debug0(STRING_DASHES)
            for artifact in token_artifacts:
                self.logger.debug0('(+) Token Artifact [ {0} with Address {1} ]'.format(artifact['name'], artifact['address']))
                self.add_token_artifact(token_artifact=artifact, alias=artifact['name'])
        self.logger.debug0(STRING_DASHES)
        self.logger.debug0('')

    def command_view_tokens(self):
        """ Command View Tokens
        This function will show the current token_data, trigger via user input command "viewTokens"
        :return:
        """
        self.logger.info(' ' + STRING_DASHES)
        self.logger.info('| {0:^13} | {1:^42} | {2:^56} | {3:^18} | '.format('Symbol', 'Address', 'Instance', 'Type'))
        self.logger.info(' ' + STRING_DASHES)
        for item in self.token_data:
            self.logger.info('| {0:^13} | {1} | {2} | {3} | '.format(
                item, self.token_data[item]['address'], self.token_data[item]['instance'], self.token_data[item]['type'])
            )
        self.logger.info(' ' + STRING_DASHES)

    def new_token_entry(self, token_address, token_instance, type_of_tokens, alias):
        """ New Token Entry
        This function will generate a new entry dict for the token_data
        :param token_address:
        :param token_instance:
        :param type_of_tokens:
        :return:
        """
        return {
            'address': token_address, 'instance': token_instance, 'type': type_of_tokens, 'name': alias
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
        else:
            self.token_data['uToken' + str(len(self.token_data))] = self.new_token_entry(token_artifact['address'], token_artifact['instance'], type_of_token, 'uToken' + str(len(self.token_data)))
