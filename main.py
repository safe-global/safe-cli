#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# number_of_elements = [
#     ([*aux_value_retainer.keys()][index], item, len(item))
#     for index, item in enumerate(aux_value_retainer.values())
# ]

from core.artifacts.token_artifacts import TokenArtifacts
from core.artifacts.account_artifacts import AccountsArtifacts
from core.artifacts.data_artifacts import DataArtifacts

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
import logging

from core.input.console_input_getter import ConsoleInputGetter
from gnosis.eth.ethereum_client import EthereumClient

from enum import Enum

class TypeOfTokens(Enum):
    ERC20 = 'ERC20'
    ERC721 = 'ERC721'


send_ether_amount = 'sendEther --address=0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e --ether=1000 --ether=2 --gwei=10'

logging_lvl = DEBUG0
logger = CustomLogger(__name__, logging_lvl)

# CustomLogger Format Definition: Output Init Configuration
formatter = logging.Formatter(fmt='[ %(levelname)s ]: %(message)s')

# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)

# Custom Logger Console/File Handler Configuration
ethereum_client = EthereumClient()
logger.addHandler(console_handler)
console_getter = ConsoleInputGetter(logger)
# ether_helper = EtherHelper(logger, ethereum_client)
#
# desired_parsed_item_list, _, _, _ = console_getter.get_gnosis_input_command_argument(send_ether_amount)
# final_amount = ether_helper.get_unify_ether_amount(desired_parsed_item_list[1:])
# print(ether_helper.get_proper_ether_amount(final_amount))

token_artifacts = TokenArtifacts(logger)
token_sample = {'address': '0x' + ('0'*40), 'instance': 'Token.Instance.Sample', 'token_type': TypeOfTokens.ERC20}
token_artifacts.add_token_artifact(token_sample, alias='OWL_TOKEN')

account_artifacts = AccountsArtifacts(logger, ethereum_client)

data_artifacts = DataArtifacts(logger, account_artifacts, None, token_artifacts, None)

stream = 'sendEther --address=gAccount.address'
desired_parsed_item_list, _, _, _ = console_getter.get_gnosis_input_command_argument(stream)

value = data_artifacts.from_alias_get_value('gAccount0.address', 'account')
token_information = data_artifacts.retrive_from_stored_values('OWL_TOKEN', None, 'token')
print('Token Information:', token_information)