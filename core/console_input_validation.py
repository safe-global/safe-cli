#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def validate_integer_input(param, param_type):
    """ Validate Integer Input

    :param param:
    :param param_type:
    :return:
    """
    # use hex()
    # address payable 160
    # address 256
    if param_type == 'uint8' and param <= 255:
        return True, ''
    elif param_type == 'uint16' and param <= 65535:
        return True, ''
    elif param_type == 'uint32' and param <= 4294967295:
        return True, ''
    elif param_type == 'uint64'and param <= 18446744073709551615:
        return True, ''
    elif param_type == 'uint128'and param <= 340282366920938463463374607431768211455:
        return True, ''
    elif param_type == 'uint160'and param <= 1461501637330902918203684832716283019655932542975:
        return True, ''
    elif param_type == 'uint256'and param <= 115792089237316195423570985008687907853269984665640564039457584007913129639935:
        return True, ''
    return False, 'Not a valid {0} (Does not fit the current type for the function input)'.format(param_type)


class ConsoleInputValidation:
    def __init__(self):
        return