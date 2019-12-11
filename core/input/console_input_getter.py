#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Aesthetic Constants
from core.constants.console_constant import QUOTE, COMMA

# Import Log Formatter
from core.logger.log_message_formatter import LogMessageFormatter


class ConsoleInputGetter:
    """ Console Input Getter
    This class will provided the necessary functions to parse and retrieve the proper values from the input user
    """
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger
        # remark: Argument Block Priorities for every Command of the Gnosis Console
        # Setup: Log Formatter
        self.log_formatter = LogMessageFormatter(self.logger)
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
                1: {'--address': 1},
            },
            'newPayload': {
                0: {'': 0},
                1: {'--alias': 1, '--from': 1, '--gas': 1, '--gasPrice': 1}
            },
            'viewNetwork': {
                0: {'': 0},
            },
            'viewAccounts': {
                0: {'': 0},
            },
            'viewContracts': {
                0: {'': 0},
            },
            'setNetwork': {
                0: {'': 0},
                1: {'--network': 1},
                2: {'--network': 1, '--api_key': 1},
            },
            'viewSender': {
                0: {'': 0},
            },
            'isOwner': {
                0: {'': 0},
                1: {'--address': 1},
            },
            'areOwners': {
                0: {'': 0},
                1: {'--address': 10},
            },
            'swapOwner': {
                0: {'': 0},
                1: {'--address': 2},
            },
            'removeOwner': {
                0: {'': 0},
                1: {'--address': 1},
            },
            'removeOwners': {
                0: {'': 0},
                1: {'--address': 10},
            },
            'addOwner': {
                0: {'': 0},
                1: {'--address': 1},
            },
            'addOwnerWithThreshold': {
                0: {'': 0},
                1: {'--address': 1, '--uint': 1},
            },
            'changeThreshold': {
                0: {'': 0},
                1: {'--uint': 1},
            },
            'loadMultipleOwner': {
                0: {'': 0},
                1: {'--address': 10},
            },
            'loadOwner': {
                0: {'': 0},
                1: {'--private_key': 1},
            },
            'unloadOwner': {
                0: {'': 0},
                1: {'--private_key': 1},
            },
            'sendEther': {
                0: {'': 0},
                1: {'--address': 1, '--private_key': 1,
                    '--wei': 10, '--kwei': 10, '--babbage': 10, '--mwei': 10, '--lovelace': 10,
                    '--picoether': 10, '--gwei': 10, '--shannon': 10, '--nanoether': 10,
                    '--szabo': 10, '--microether': 10, '--micro': 10, '--finney': 10,
                    '--milliether': 10, '--milli': 10, '--ether': 10, '--kether': 10,
                    '--grand': 10, '--mether': 10, '--gether': 10, '--tether': 10}
            },
            'depositEther': {
                0: {'': 0},
                1: {'--private_key': 1,
                    '--wei': 10, '--kwei': 10, '--babbage': 10, '--mwei': 10, '--lovelace': 10,
                    '--picoether': 10, '--gwei': 10, '--shannon': 10, '--nanoether': 10,
                    '--szabo': 10, '--microether': 10, '--micro': 10, '--finney': 10,
                    '--milliether': 10, '--milli': 10, '--ether': 10, '--kether': 10,
                    '--grand': 10, '--mether': 10, '--gether': 10, '--tether': 10}
            },
            'withdrawEther': {
                0: {'': 0},
                1: {'--address': 1,
                    '--wei': 10, '--kwei': 10, '--babbage': 10, '--mwei': 10, '--lovelace': 10,
                    '--picoether': 10, '--gwei': 10, '--shannon': 10, '--nanoether': 10,
                    '--szabo': 10, '--microether': 10, '--micro': 10, '--finney': 10,
                    '--milliether': 10, '--milli': 10, '--ether': 10, '--kether': 10,
                    '--grand': 10, '--mether': 10, '--gether': 10, '--tether': 10}
            },
            'sendToken': {
                0: {'': 0},
                1: {'--address': 2, '--amount': 1, '--private_key': 1},
            },
            'depositToken': {
                0: {'': 0},
                1: {'--address': 1, '--amount': 1, '--private_key': 1},
            },
            'withdrawToken': {
                0: {'': 0},
                1: {'--address': 2, '--amount': 1},
            },
            'updateSafe': {
                0: {'': 0},
                1: {'--address': 1},
            },
        }

    @staticmethod
    def get_size_of_priority_group(priority_group):
        """ Get Size Of Priority Group
        This function will get the current size of the priority group
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

    def _get_input_console_arguments(self, stream, splitter=' '):
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
            self.logger.error('_get_input_console_arguments unable to properly parse the stream {0}'.format(err))
            return '', []

    def _get_method_argument_value(self, value, quote=True):
        """ Get Method Argument Value
        This function will split the contents of the input param and give the value
        :param value:
        :return:
        """
        if quote:
            return self._get_quoted_argument(value.split('=')[1])
        return value.split('=')[1]

    def get_input_method_arguments(self, argument_list, function_arguments):
        """ Get Input Method Arguments
        This method will in charge to evaluate how to process the current operation been provided via input string
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
                    self.logger.warn('--queue|--query value already parsed, this value will be ignored')
                else:
                    execute_value = True
            elif '--query' == argument_item:
                if execute_value or to_queue:
                    self.logger.warn('--execute|--queue value already parsed, this value will be ignored')
                else:
                    to_query = True
            elif '--queue' == argument_item:
                if execute_value or to_query:
                    self.logger.warn('--execute|--query value already parsed, this value will be ignored')
                else:
                    to_queue = True
            else:
                for sub_index, argument_type in enumerate(function_arguments):
                    if argument_type[sub_index] in argument_item \
                            and argument_positions_to_fill != 0 \
                            and argument_positions_to_fill > argument_positions_filled:
                        arguments_to_fill += self._get_method_argument_value(argument_item) + COMMA
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
            '--address': [], '--alias': [], '--bytecode': [], '--uint': [],
            '--gas': [], '--gasPrice': [], '--from': [], '--private_key': [], '--api_key': [], '--amount': [],
            '--wei': [], '--kwei': [], '--babbage': [], '--mwei': [], '--lovelace': [],
            '--picoether': [], '--gwei': [], '--shannon': [], '--nanoether': [], '--szabo': [],
            '--microether': [], '--micro': [], '--finney': [], '--milliether': [], '--milli': [],
            '--ether': [], '--kether': [], '--grand': [], '--mether': [], '--gether': [], '--tether': [], '--network':[]
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
        This function will retrieve the values from any given and known priority group provided by the user via input
        string
        :param priority_groups:
        :param parsed_arguments:
        :return: desired_parsed_item_list
        """
        access_counter = []
        error_counter = []
        parsed_item_counter = []
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
            parsed_item_counter.append(desired_parse_items_count)
            error_counter.append(error_count)
            access_counter.append(access_count)

        selected_priority_group = parsed_item_counter.index(max(parsed_item_counter))
        size_of_selected_priority_group = self.get_size_of_priority_group(priority_groups[selected_priority_group])
        self.logger.debug0(
            '| Access Counters: {0} | Error Counters: {1} '
            '| Desired Items Counters: {2} | Total Desired Items: [ {3} ]'.format(
                access_counter, error_counter, parsed_item_counter, size_of_selected_priority_group)
        )

        # Here since we know where to look for in the input data, the only thing that's left is to make a final sweep
        # and pick de values we are searching for
        for parsed_item in priority_groups[selected_priority_group]:
            tmp_index = int(priority_groups[selected_priority_group][parsed_item])
            desired_parsed_item_list.append((parsed_item, parsed_arguments[parsed_item][:tmp_index]))

        return desired_parsed_item_list, parsed_item_counter.index(max(parsed_item_counter))

    def get_gnosis_input_command_argument(self, stream):
        """ Get Gnosis Input Command Arguments
        This function will get the input stream arguments provided in the gnosis-cli and split them in a list with the
        desired values based on a priority list defined within the class
        :param stream: String input value
        :return: desired_parsed_item_list, priority_group, command_argument, argument_list
        """
        command_argument, argument_list = self._get_input_console_arguments(stream)
        desired_parsed_item_list, priority_group = self.evaluate_arguments_based_on_priority(command_argument, argument_list)
        if priority_group == -1:
            priority_groups = {-1: 'None'}
        else:
            priority_groups = self.argument_block_priorities[command_argument][priority_group]
        self.logger.debug0('----------' * 14)
        self.logger.debug0('| Command: {0} | Argument: {1} | '.format(command_argument, argument_list))
        self.logger.debug0('| Priority Group: {0} | Group Values: {1} | '.format(priority_group, priority_groups))
        self.logger.debug0('| Argument Resolution: {0} |  '.format(desired_parsed_item_list))
        self.logger.debug0('----------' * 14)
        return desired_parsed_item_list, priority_group, command_argument.lstrip(), argument_list
