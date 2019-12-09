#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Prompt Toolkit Modules
from prompt_toolkit import HTML, prompt

from core.constants.console_constant import (
    STRING_DASHES, payload_options, payload_tx_options
)


class PayloadArtifacts:
    """ Payload Artifacts
    This class will store the payload_artifacts for the console
    """
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger
        self.payload_data = {}

    def command_view_payloads(self):
        """ Command View Payloads
        This function will prompt the current state of the payload_artifact if the command viewPayloads is provided
        by the user
        :return:
        """
        self.logger.info(' ' + STRING_DASHES)
        self.logger.info('| {0:^14} | {1:^121} |'.format('Alias', 'Payload'))
        self.logger.info(' ' + STRING_DASHES)
        self.logger.debug0(STRING_DASHES)
        for item in self.payload_data:
            self.logger.info('| {0:^14} | {1:^121} |'.format(item, self.payload_data[item]['payload']))
        self.logger.info(' ' + STRING_DASHES)

    def command_new_payload(self, command_argument, argument_list):
        """ Command New Payload
        This function will launch the proper prompt for building a new custom payload
        :param command_argument:
        :param argument_list:
        :return:
        """
        if command_argument == 'newPayload' and argument_list == []:
            alias, composed_payload = self._new_payload_helper(payload_options)
            print('newPayload:', alias, composed_payload)
            return self.add_payload_artifact(composed_payload, alias)

        elif command_argument == 'newTxPayload' and argument_list == []:
            alias, composed_payload = self._new_payload_helper(payload_tx_options)

            return self.add_payload_artifact(composed_payload, alias)
        else:
            print('input for argument --nonce=, --gas=, --gasPrice=, --value=')

    def new_payload_entry(self, payload_artifact, alias):
        """ New Payload Entry
        This function will generate a new entry dict for the payload_data
        :param payload_artifact:
        :param alias:
        :return:
        """
        return {'name': alias, 'payload': payload_artifact}

    def add_payload_artifact(self, payload_artifact, alias=''):
        """ Add Payload Artifact
        This function will add a new payload_artifact to the payload_data dict
        :param payload_artifact:
        :param alias:
        :return:
        """
        if alias != '':
            self.payload_data[alias] = self.new_payload_entry(payload_artifact, alias)
            return self.payload_data
        self.payload_data['uPayload' + str(len(self.payload_data))] = self.new_payload_entry(payload_artifact, 'uPayload_' + str(len(self.payload_data)))
        return self.payload_data

    @staticmethod
    def _new_payload_helper(payload_options):
        """ New Payload Helper
        This function will trigger the behaviour for the newPayload, when the --inputs are None
        :param payload_options:
        :return:
        """
        alias = ''
        compose_answer = '{'
        for item in payload_options:
            text = ('\'%s\' : ' % (item)).rjust(20)
            answer = prompt(HTML((' <strong>%s</strong> ') % text))
            if answer == '':
                if (item == 'gas') or (item == 'gasPrice') or (item == 'nonce') or (item == 'safe_tx_gas'):
                    compose_answer += '\'%s\' : %s' % (item, str(0)) + ', '
                elif item == 'alias':
                    continue
                else:
                    # todo: here check if setDefaultSender is active, if it's empty, fill the current defaultOwner
                    #  same goes if you put defaultOwner this should be transcribed to the proper address
                    compose_answer += '\'%s\' : \'%s\'' % (item, '') + ', '
            else:
                if item == 'alias':
                    alias = answer
                else:
                    compose_answer += '\'%s\' : %s' % (item, answer) + ', '
        return alias, compose_answer[:-2] + '}'
