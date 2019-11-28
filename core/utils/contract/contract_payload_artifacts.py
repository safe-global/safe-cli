from prompt_toolkit import HTML, prompt

payload_options = ['alias', 'from', 'gas', 'gasPrice']
payload_tx_options = ['alias', 'from', 'gas', 'gasPrice', 'value', 'nonce', 'safe_tx_gas']

class ContractPayloadArtifacts:
    def __init__(self):
        self.payload_data = {}

    def add_payload(self, payload_artifact, alias=''):
        if alias != '':
            self.payload_data[alias] = {'payload': payload_artifact}
            return self.payload_data
        self.payload_data['uPayload' + str(len(self.payload_data))] = {'payload': payload_artifact}
        return self.payload_data

    def get_payload_from_alias(self, alias, key=None):
        try:
            if key is None:
                return self.payload_data[alias]
            return self.payload_data[alias]['payload']
        except KeyError:
            raise KeyError
        except Exception as err:
            print(type(err), err)

    @staticmethod
    def _new_payload_helper(payload_options):
        alias = ''
        compose_answer = '{'
        for item in payload_options:
            text = ('\'%s\' : ' % (item)).rjust(20)
            answer = prompt(HTML(' <strong>%s</strong> ') % text)
            if answer == '':
                if (item == 'gas') or (item == 'gasPrice') or (item == 'nonce') or (item == 'safe_tx_gas'):
                    compose_answer += '\'%s\' : %s' % (item, str(0)) + ', '
                elif item == 'alias':
                    continue
                else:
                    # todo: here check if setDefaultOwner is active, if it's empty, fill the current defaultOwner
                    #  same goes if you put defaultOwner this should be transcribed to the proper address
                    compose_answer += '\'%s\' : \'%s\'' % (item, '') + ', '
            else:
                if item == 'alias':
                    alias = answer
                else:
                    compose_answer += '\'%s\' : %s' % (item, answer) + ', '

        return alias, compose_answer[:-2] + '}'

    def command_view_payloads(self):
        for item in self.payload_data:
            print(item, self.payload_data[item])

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
            return self.add_payload(composed_payload, alias)

        elif command_argument == 'newTxPayload' and argument_list == []:
            alias, composed_payload = self._new_payload_helper(payload_tx_options)

            return self.add_payload(composed_payload, alias)
        else:
            print('input for argument --nonce=, --gas=, --gasPrice=, --value=')
