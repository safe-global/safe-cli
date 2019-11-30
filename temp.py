#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

from core.artifacts.console_token_artifacts import ConsoleTokenArtifacts
from core.artifacts.console_contract_artifacts import ConsoleContractArtifacts

logging_lvl = INFO
logger = CustomLogger(__name__, logging_lvl)

# CustomLogger Format Definition: Output Init Configuration
formatter = logging.Formatter(fmt='%(asctime)s - [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Custom Logger File Configuration: File Init Configuration
file_handler = logging.FileHandler('./log/gnosis_console/general_console.log', 'w')
file_handler.setFormatter(formatter)
file_handler.setLevel(level=logging_lvl)

# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)

# Custom Logger Console/File Handler Configuration
logger.addHandler(file_handler)
logger.addHandler(console_handler)

console_contract_artifacts = ConsoleContractArtifacts()
console_token_artifacts = ConsoleTokenArtifacts(logger)

import gnosis
from enum import Enum


class TypeOfContract(Enum):
    STANDARD = 'STANDARD'
    ERC20 = 'ERC20'
    ERC721 = 'ERC721'


from core.utils.contract_reader import ContractReader


def contract_instance_loader(address, abi_path, contract_type):
    # Add them to the proper list, based on a given type provided by the console engine via command
    contract_reader = ContractReader(logger)
    contract_abi, contract_bytecode, contract_name = contract_reader.read_from(abi_path)

    # if contract_type is TypeOfContract.STANDARD:
    #     # Add to the ContractArtifacts data
    # elif contract_type is TypeOfContract.ERC20 or contract_type == TypeOfContract.ERC721:
    #     # Add to the TokenArtifact data

    return
