#!/usr/bin/env python3
# -*- coding: utf-8 -*-

QUOTE = '\''
COMA = ','

class ConsoleInputGetter:
    def __init__(self):
        self.name = self.__class__.__name__

        self.argument_block_priorities = {
            'newContract': {
                0: {'--address': 1, '--abi=': 1}
            },
            'loadContract': {
                0: {'--alias': 1},
                1: {'--address': 1}
            },
            'loadSafe': {
                0: {'--alias': 1},
                1: {'--address': 1}
            },
            'newAccount': {
                0: {'': 0},
                1: {'--private_key': 1},
                2: {'--address': 1, '--private_key': 1}},
            'newToken': {
                0: {'': 0},
                1: {'--address': 1}},
            'newPayload': {
                0: {'': 0},
                1: {'--alias': 1, '--from': 1, '--gas': 1, '--gasPrice': 1}
            },
            'dummyCommand': {
                0: {'': 0},
                1: {'--address': 3, '--gas': 1},
                2: {'--gas': 3}
            },
        }


    @staticmethod
    def _get_quoted_argument(value):
        """ Quote Argument
        This functions quotes a value
        :param value:
        :return:
        """
        return QUOTE + value + QUOTE

    def _get_method_argument_value(self, value, quote=True):
        """ Get Method Argument Value

        :param value:
        :return:
        """
        if quote:
            return self._get_quoted_argument(value.split('=')[1])
        return value.split('=')[1]

    @staticmethod
    def _get_input_console_arguments(stream, splitter=' '):
        argument_list = []
        command_argument = ''

        try:
            splitted_stream = stream.split(splitter)
            command_argument = splitted_stream[0]
            argument_list = splitted_stream[1:]
            return command_argument, argument_list
        except IndexError as err:
            print('_get_input_console_arguments unable to properly parse', type(err), err)
            return command_argument, argument_list

    # < >
    def get_size_of_priority_group(self, priority_group):
        value = 0
        for elements in priority_group:
            value += int(priority_group[elements])
        return value

    def _get_arguments_based_on_priority(self, command_argument, argument_list):
        """ Get Arguments Based on Priority
        This function will evaluate the dict of argument priority and retrieve the proper values, once the max
        amount of arguments based on types it's filled the proper command will be triggered by the console
        :param command_argument:
        :param argument_list:
        :return:
        """
        priority_groups = self.argument_block_priorities[command_argument]
        valid_arguments = []
        priority_group = -1
        aux_value_retainer = {
            '--address': [], '--alias': [], '--bytecode': [],
            '--gas': [], '--gasPrice': [], '--from': [], '--private_key': []
        }

        print('Get User Input Based On Argument Priority')
        print('----------' * 10)
        aux = {}
        #for element_index in priority_groups:
        for argument_item in argument_list:
            # Get the param_type and value contents of the current argument item, with splitter '='
            param_type, value = self._get_input_console_arguments(argument_item, '=')
            try:
                aux_value_retainer[param_type].append(value[0])
            except KeyError:
                continue

        final_dict = {}
        for group in priority_groups.values():
            for sub_item in group.keys():
                if sub_item == '':
                    continue
                else:
                    print(sub_item, group[sub_item])
                    final_dict[sub_item] = aux_value_retainer[sub_item][:(group[sub_item] - 1)]
                print(final_dict[sub_item])

        print(final_dict)
        return valid_arguments, priority_group

    def get_gnosis_input_command_argument(self, command_argument, argument_list, checklist):
        """ Get Gnosis Input Command Arguments
        This function will get the input arguments provided in the gnosis-cli

        :param command_argument:
        :param argument_list:
        :param checklist:
        :return:
        """
        print('Command:', command_argument, 'Argument_List:', argument_list)
        valid_arguments, priority_group = self._get_arguments_based_on_priority(command_argument, argument_list)
        print('valid_arguments:', valid_arguments, 'priority_group:', priority_group)
        # for sub_index, argument_item in enumerate(argument_list):
        #     if argument_item.startswith('--alias='):
        #         alias = self._get_method_argument_value(argument_item, quote=False)
        #         # alias = self._get_method_argument_value(argument_item, quote=False)
        #         return alias
        #     elif argument_item.startswith('--name='):
        #         name = self._get_method_argument_value(argument_item, quote=False)
        #         return name
        #     elif argument_item.startswith('--id='):
        #         id = self._get_method_argument_value(argument_item, quote=False)
        #     elif argument_item.startswith('--abi='):
        #         contract_abi = self._get_method_argument_value(argument_item, quote=False)
        #     elif argument_item.startswith('--address='):
        #         tmp_address = self._get_method_argument_value(argument_item, quote=False)
        #         #aux_tmp_address = self._eval_stored_arguments(tmp_address, self.console_accounts.account_data)
        #         # aux2_tmp_address = self._eval_stored_arguments(tmp_address, self.contract_console_data.contract_data)
        #         #print(aux_tmp_address)
        #     elif argument_item.startswith('--bytecode='):
        #         contract_bytecode = self._get_method_argument_value(argument_item, quote=False)
        #     else:
        #         continue
        #     print(' (+) Argument:', argument_item)
