#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Aesthetic Constants
from core.constants.console_constant import STRING_DASHES

# Import Enum with TypeOfToken
from core.artifacts.constants.type_artifacts import TypeOfTokens

# Import Prompt Toolkit Modules
from prompt_toolkit import HTML, prompt

# Import ERC20Contract, ERC721Contract
from gnosis.eth.contracts import (
    get_erc20_contract, get_erc721_contract
)

# Token Options
token_options = ['type', 'address']


class TokenArtifacts:
    """ Token Artifacts
    This class will store the token_artifacts for the console
    """
    def __init__(self, logger, ethereum_client):
        self.logger = logger
        self.ethereum_client = ethereum_client
        self.token_data = {}

    def pre_load_erc20_artifacts(self, token_erc20_artifacts):
        """ Pre Load Artifacts
        This function will pre-load any provided erc20 tokens, during the launching process of the general console
        gnosis-cli.
        :param token_erc20_artifacts:
        :return:
        """
        if token_erc20_artifacts:
            self.logger.debug0('')
            self.logger.debug0(' | Setup Token ERC20 Artifacts  | ')
            self.logger.debug0(STRING_DASHES)

            for token_erc20_address in token_erc20_artifacts:
                if self.ethereum_client.w3.isAddress(token_erc20_address):
                    try:
                        token_instance = get_erc20_contract(self.ethereum_client.w3, token_erc20_address)
                        token_alias = token_instance.functions.symbol().call()
                        token_artifact = self.new_token_entry(
                            token_erc20_address, token_instance,  TypeOfTokens.ERC20, token_alias)
                        self.logger.info('(+) Token ERC20 Artifact [ {0} with Address {1} ]'.format(
                            token_artifact['name'], token_artifact['address']))
                        self.add_token_artifact(token_artifact, token_artifact['name'])
                    except Exception as err:
                        self.logger.error(err)
                        self.logger.error('Unable to get erc20 contract, are you sure this is a valid token address?')
                else:
                    self.logger.error('Address for erc20 token is not valid')
        self.logger.debug0(STRING_DASHES)
        self.logger.debug0('')

    def pre_load_erc721_artifacts(self, token_erc721_artifacts):
        """ Pre Load Artifacts
        This function will pre-load any provided erc721 tokens, during the launching process of the general console
        gnosis-cli.
        :param token_erc721_artifacts:
        :return:
        """
        if token_erc721_artifacts:
            self.logger.debug0('')
            self.logger.debug0(' | Setup Token ERC721 Artifacts  | ')
            self.logger.debug0(STRING_DASHES)

            for token_erc721_address in token_erc721_artifacts:
                if self.ethereum_client.w3.isAddress(token_erc721_address):
                    try:
                        token_instance = get_erc721_contract(self.ethereum_client.w3, token_erc721_address)
                        token_alias = token_instance.functions.symbol().call()
                        token_artifact = self.new_token_entry(
                            token_erc721_address, token_instance, TypeOfTokens.ERC721, token_alias)
                        self.logger.info('(+) Token ERC721 Artifact [ {0} with Address {1} ]'.format(
                            token_artifact['name'], token_artifact['address']))
                        self.add_token_artifact(token_artifact, token_artifact['name'])
                    except Exception as err:
                        self.logger.error(err)
                        self.logger.error('Unable to get erc721 contract, are you sure this is a valid token address?')
                else:
                    self.logger.error('Address for erc721 token is not valid')
        self.logger.debug0(STRING_DASHES)
        self.logger.debug0('')

    def command_new_token(self, command_argument, argument_list):
        """ Command New Token
        This function will launch the proper prompt for building a new token
        :param command_argument:
        :param argument_list:
        :return:
        """
        if command_argument == 'newToken' and argument_list == []:
            new_token_entry = self._new_token_helper(token_options)
            self.logger.info('newToken: ' + str(new_token_entry))
            return self.add_token_artifact(new_token_entry, new_token_entry['name'])
        else:
            self.logger.info('newToken and complete the input requirements')

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
                item, self.token_data[item]['address'],
                self.token_data[item]['instance'], self.token_data[item]['type'])
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

    def add_token_artifact(self, token_artifact, alias=''):
        """
        This function will add a new token_artifact to the token_data dict
        :param token_artifact:
        :param alias:
        :return:
        """
        if alias != '':
            self.token_data[alias] = self.new_token_entry(
                token_artifact['address'], token_artifact['instance'], token_artifact['type'], token_artifact['name'])
        else:
            self.token_data['uToken' + str(len(self.token_data))] = self.new_token_entry(
                token_artifact['address'], token_artifact['instance'], token_artifact['type'], token_artifact['name'])

    def _new_token_helper(self, token_options):
        """ New Token Helper
        This function will trigger the behaviour for the newToken, when the --inputs are None
        :param token_options:
        :return:
        """
        token_type = None
        token_instance = None
        token_alias = None
        token_address = None
        for item in token_options:
            text = ('%s : ' % (item)).rjust(20)
            token_answer = prompt(HTML((' <strong>%s</strong> ') % text.title()))
            if item == 'type':
                if token_answer == 'ERC20':
                    token_type = TypeOfTokens.ERC20
                elif token_answer == 'ERC721':
                    token_type = TypeOfTokens.ERC721
                else:
                    self.logger.error('Type must be selected before doing anything')

            elif item == 'address':
                if self.ethereum_client.w3.isAddress(token_answer):
                    if token_type == TypeOfTokens.ERC20:
                        try:
                            token_address = token_answer
                            token_instance = get_erc20_contract(self.ethereum_client.w3, token_answer)
                            token_alias = token_instance.functions.symbol().call()
                        except Exception as err:
                            self.logger.error(err)
                            self.logger.error('Unable to get erc20 contract, are you sure this is a valid token address?')
                    elif token_type == TypeOfTokens.ERC721:
                        try:
                            token_address = token_answer
                            token_instance = get_erc721_contract(self.ethereum_client.w3, token_answer)
                            token_alias = token_instance.functions.symbol().call()
                        except Exception as err:
                            self.logger.error(err)
                            self.logger.error('Unable to get erc721 contract, are you sure this is a valid token address?')
                else:
                    self.logger.error('Address is not valid')

        return self.new_token_entry(token_address, token_instance, token_type, token_alias)


