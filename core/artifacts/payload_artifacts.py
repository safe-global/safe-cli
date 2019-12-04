#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Prompt Toolkit Modules
from prompt_toolkit import HTML, prompt

# Constants
payload_options = ['alias', 'from', 'gas', 'gasPrice']
payload_tx_options = ['alias', 'from', 'gas', 'gasPrice', 'value', 'nonce', 'safe_tx_gas']
STRING_DASHES = '---------' * 10


class PayloadArtifacts:
    def __init__(self, logger):
        self.logger = logger
        self.payload_data = {}

    def command_view_payloads(self):
        self.logger.debug0(STRING_DASHES)
        for item in self.payload_data:
            self.logger.info(' | {0:^15} | {1:^25} '.format(item, self.payload_data[item]['name']))
        self.logger.debug0(STRING_DASHES)

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
        return {'name': alias, 'payload': payload_artifact}

    def add_payload_artifact(self, payload_artifact, alias=''):
        if alias != '':
            self.payload_data[alias] = self.new_payload_entry(payload_artifact, alias)
            return self.payload_data
        self.payload_data['uPayload' + str(len(self.payload_data))] = self.new_payload_entry(payload_artifact, 'uPayload_' + str(len(self.payload_data)))
        return self.payload_data

    @staticmethod
    def _new_payload_helper(payload_options):
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


