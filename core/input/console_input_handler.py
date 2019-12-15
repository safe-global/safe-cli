#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ConsoleInputHandler:
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

    def input_handler(self, command_argument, desired_parsed_item_list, priority_group):
        if command_argument == 'loadContract':
            if priority_group == 0:
                contract_alias = desired_parsed_item_list[0][1][0]
                return contract_alias
        elif command_argument == 'loadSafe':
            if priority_group == 1:
                safe_address = desired_parsed_item_list[0][1][0]
                return safe_address
        elif command_argument == 'setNetwork':
            if priority_group == 1:
                network_name = desired_parsed_item_list[0][1][0]
                network_api_key = None
                return network_name, network_api_key
            elif priority_group == 2:
                network_name = desired_parsed_item_list[0][1][0]
                network_api_key = desired_parsed_item_list[1][1][0]
                return network_name, network_api_key
        elif command_argument == 'isOwner':
            if priority_group == 1:
                owner_address = desired_parsed_item_list[0][1][0]
                return owner_address
        elif command_argument == 'changeThreshold':
            if priority_group == 1:
                new_threshold = int(desired_parsed_item_list[0][1][0])
                return new_threshold
        elif command_argument == 'addOwnerWithThreshold':
            if priority_group == 1:
                new_owner_address = desired_parsed_item_list[0][1][0]
                new_threshold = int(desired_parsed_item_list[1][1][0])
                return new_owner_address, new_threshold
        elif command_argument == 'addOwner':
            if priority_group == 1:
                new_owner_address = desired_parsed_item_list[0][1][0]
                return new_owner_address
        elif command_argument == 'removeOwner':
            if priority_group == 1:
                old_owner_address = desired_parsed_item_list[0][1][0]
                return old_owner_address
        elif command_argument == 'swapOwner' or command_argument == 'changeOwner':
            if priority_group == 1:
                old_owner_address = desired_parsed_item_list[0][1][0]
                new_owner_address = desired_parsed_item_list[0][1][1]
                return old_owner_address, new_owner_address
        elif command_argument == 'sendToken':
            if priority_group == 1:
                token_address = desired_parsed_item_list[0][1][0]
                address_to = desired_parsed_item_list[1][1][0]
                token_amount = int(desired_parsed_item_list[2][1][0])
                private_key = desired_parsed_item_list[3][1][0]
                print(token_address, address_to, token_amount, private_key)
                return token_address, address_to, token_amount, private_key
        elif command_argument == 'depositToken':
            if priority_group == 1:
                token_address = desired_parsed_item_list[0][1][0]
                token_amount = int(desired_parsed_item_list[1][1][0])
                private_key = desired_parsed_item_list[2][1][0]
                return token_address, token_amount, private_key
        elif command_argument == 'withdrawToken':
            if priority_group == 1:
                token_address = desired_parsed_item_list[0][1][0]
                address_to = desired_parsed_item_list[1][1][0]
                token_amount = int(desired_parsed_item_list[2][1][0])
                return token_address, address_to, token_amount
        elif command_argument == 'sendEther':
            if priority_group == 1:
                address_to = desired_parsed_item_list[0][1][0]
                private_key = desired_parsed_item_list[1][1][0]
                ethereum_amounts = desired_parsed_item_list[2:]
                return address_to, private_key, ethereum_amounts
        elif command_argument == 'depositEther':
            if priority_group == 1:
                private_key = desired_parsed_item_list[0][1][0]
                ethereum_amounts = desired_parsed_item_list[1:]
                return private_key, ethereum_amounts
        elif command_argument == 'withdrawEther':
            if priority_group == 1:
                address_to = desired_parsed_item_list[0][1][0]
                ethereum_amounts = desired_parsed_item_list[1:]
                return address_to, ethereum_amounts
        elif command_argument == 'updateSafe':
            if priority_group == 1:
                new_master_copy_address = desired_parsed_item_list[0][1][0]
                return new_master_copy_address
        elif command_argument == 'loadOwner':
            if priority_group == 1:
                private_key = desired_parsed_item_list[0][1][0]
                return private_key
        elif command_argument == 'unloadOwner':
            if priority_group == 1:
                private_key = desired_parsed_item_list[0][1][0]
                return private_key