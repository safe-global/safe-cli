#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Enum Packages
from enum import Enum

# String Size Of Diferent Type of Addresses
CONTRACT_ADDRESS_LENGTH = 42
TX_ADDRESS_LENGTH = 66

# String Size of API Keys
INFURA_API_KEY_LENGTH = 32
ETHERSCAN_API_KEY_LENGTH = 34


class ConsoleSessionTypeFlag(Enum):
    MAIN_CONSOLE_SESSION = '0'
    CONTRACT_CONSOLE_SESSION = '1'


