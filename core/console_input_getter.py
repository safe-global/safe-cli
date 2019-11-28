#!/usr/bin/env python3
# -*- coding: utf-8 -*-

QUOTE = '\''
COMA = ','


class ConsoleInputGetter:
    def __init__(self):
        self.name = self.__class__.__name__
        # remark: Argument Block Priorities for every Command
        self.argument_block_priorities = {
            'newContract': {
                0: {'--address': 1, '--abi': 1}
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
                2: {'--address': 1, '--private_key': 1}
            },
            'newToken': {
                0: {'': 0},
                1: {'--address': 1}
            },
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
    def get_size_of_priority_group(priority_group):
        """ Get Size Of Priority Group

        :param priority_group:
        :return:
        """
        value = 0
        for elements in priority_group:
            value += int(priority_group[elements])
        return value

    @staticmethod
    def _get_quoted_argument(value):
        """ Get Quote Argument
        This functions quotes a value
        :param value:
        :return:
        """
        return QUOTE + value + QUOTE

    @staticmethod
    def _get_input_console_arguments(stream, splitter=' '):
        """ Get Input Console Arguments
        This Function will split based on a given splitter, and return command_trigger and argument_list
        :param stream: command stream input provided by the user
        :param splitter: command splitter provided by the user, default value it's white space
        :return:
        """
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

    def _get_stored_arguments(self, argument_item, storage_item):
        stored_index = argument_item.split('.')
        print('stored_argument', stored_index[0], stored_index[1])
        try:
            tmp_address = storage_item[stored_index[0]][stored_index[1]]
            return tmp_address
        except KeyError as err:
            print('Key Error here', err)

    def _get_method_argument_value(self, value, quote=True):
        """ Get Method Argument Value

        :param value:
        :return:
        """
        if quote:
            return self._get_quoted_argument(value.split('=')[1])
        return value.split('=')[1]

    def get_input_method_arguments(self, argument_list, function_arguments):
        """ Get Input Method Arguments

        :param argument_list:
        :param function_arguments:
        :return:
        """
        arguments_to_fill = ''
        execute_value = False
        to_queue = False
        to_query = False
        address_from = ''

        # Control for number of input arguments
        argument_positions_to_fill = len(function_arguments)
        argument_positions_filled = 0

        for sub_index, argument_item in enumerate(argument_list):
            if '--from=' in argument_item:
                address_from = self._get_method_argument_value(argument_item)
            elif '--execute' == argument_item:
                if to_queue or to_query:
                    print('--queue|--query value already parsed, this value will be ignored')
                else:
                    execute_value = True
            elif '--query' == argument_item:
                if execute_value or to_queue:
                    print('--execute|--queue value already parsed, this value will be ignored')
                else:
                    to_query = True
            elif '--queue' == argument_item:
                if execute_value or to_query:
                    print('--execute|--query value already parsed, this value will be ignored')
                else:
                    to_queue = True
            else:
                for sub_index, argument_type in enumerate(function_arguments):
                    if argument_type[sub_index] in argument_item \
                            and argument_positions_to_fill != 0 \
                            and argument_positions_to_fill > argument_positions_filled:
                        arguments_to_fill += self._get_method_argument_value(argument_item) + COMA
                        argument_positions_filled += 1

                arguments_to_fill = arguments_to_fill[:-1]

        return argument_list[0], arguments_to_fill, address_from, execute_value, to_queue, to_query

    def evaluate_arguments_based_on_priority(self, command_argument, argument_list):
        """ Get Arguments Based on Priority
        This function will evaluate the dict of argument priority and retrieve the proper values, once the max
        amount of arguments based on types it's filled the proper command will be triggered by the console
        :param command_argument:
        :param argument_list:
        :return:
        """
        selected_priority = -1
        aux_value_retainer = {
            '--address': [], '--alias': [], '--bytecode': [],
            '--gas': [], '--gasPrice': [], '--from': [], '--private_key': []
        }
        try:
            priority_groups = self.argument_block_priorities[command_argument]
            for argument_item in argument_list:
                # Get the param_type and value contents of the current argument item, with splitter '='
                param_type, value = self._get_input_console_arguments(argument_item, '=')
                try:
                    # Add every new value found in the user input
                    aux_value_retainer[param_type].append(value[0])
                except KeyError:
                    continue
            return self.get_arguments_based_on_priority(priority_groups, aux_value_retainer)
        except KeyError:
            return aux_value_retainer, selected_priority

    def get_arguments_based_on_priority(self, priority_groups, parsed_arguments):
        """ Get Arguments Based On Priority

        :param priority_groups:
        :param parsed_arguments:
        :return:
        """
        access_counter = []
        error_counter = []
        desired_parse_item_list = []
        desired_parsed_item_list = []
        for index_group in priority_groups:
            error_count = 0
            access_count = 0
            desired_parse_items_count = 0
            for parsed_item in parsed_arguments:
                try:
                    # Number of Desired Elements of a param_type --address, --alias ...
                    desired_data_size = int(priority_groups[index_group][parsed_item])
                    # Only when the Number of Elements in the Input Matches or is More than the
                    # Number of Desired Elements of a param_type
                    if len(parsed_arguments[parsed_item]) >= desired_data_size and parsed_item in priority_groups[index_group]:
                        # This Data Access is here to force the KeyError Exception so another iteration can
                        # be triggered, without adding
                        data = parsed_arguments[parsed_item][:desired_data_size]
                        # Items of Desired Data Found
                        desired_parse_items_count += len(data)
                        # access_count: metric for debugging
                        access_count += 1
                except KeyError:
                    # access_count: metric for debugging
                    error_count += 1
                    continue

            # Since the only time the functions add's the number to the counters it's when the process is complete
            desired_parse_item_list.append(desired_parse_items_count)
            error_counter.append(error_count)
            access_counter.append(access_count)

        selected_priority_group = desired_parse_item_list.index(max(desired_parse_item_list))
        size_of_selected_priority_group = self.get_size_of_priority_group(priority_groups[selected_priority_group])
        print('| Access Counters:', access_counter, '| Error Counters:', error_counter,
              '| Desired Items Counters:', desired_parse_item_list, '| Total Desired Items', size_of_selected_priority_group, '| ')

        # Here since we know where to look for in the input data, the only thing that's left is to make a final sweep
        # and pick de values we are searching for
        for parsed_item in priority_groups[selected_priority_group]:
            tmp_index = int(priority_groups[selected_priority_group][parsed_item])
            desired_parsed_item_list.append((parsed_item, parsed_arguments[parsed_item][:tmp_index]))

        return desired_parsed_item_list, desired_parse_item_list.index(max(desired_parse_item_list))

    def get_gnosis_input_command_argument(self, stream, checklist=[]):
        """ Get Gnosis Input Command Arguments
        This function will get the input arguments provided in the gnosis-cli

        :param command_argument:
        :param argument_list:
        :param checklist:
        :return:
        """
        command_argument, argument_list = self._get_input_console_arguments(stream)
        print('+' + '---------' * 10 + '+')
        print('| Command:', command_argument, '| Argument:', argument_list, '| ')
        desired_parsed_item_list, priority_group = self.evaluate_arguments_based_on_priority(command_argument, argument_list)
        print('| Argument Resolution:', desired_parsed_item_list, '| Priority Group:', priority_group, '| ')
        print('+' + '---------' * 10 + '+')
        return desired_parsed_item_list, priority_group, command_argument, argument_list

