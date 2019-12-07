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
from gnosis.eth.ethereum_client import EthereumClient, Erc20Manager
from hexbytes import HexBytes


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


# def send_ether(address_to, wei_amount, private_key):
#     tx_hash = ethereum_client.send_eth_to(HexBytes(private_key).hex(), address_to, ethereum_client.w3.eth.gasPrice, wei_amount)
#     tx_receipt = ethereum_client.get_transaction_receipt(tx_hash, timeout=60)
#     print(tx_receipt)
#     return tx_receipt

# sendEther --address=0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0 --ether=2
# depositEther --ether=2

erc20_manager = Erc20Manager(ethereum_client, 10)
from eth_account import Account


def send_ether_raw(address_to, wei_amount, private_key):
    """ Send Ether Raw
    This function will send ether to the address_to, wei_amount, private_key
    :param address_to:
    :param wei_amount:
    :param private_key:
    :return:
    """
    local_account = Account.privateKeyToAccount(private_key)
    signed_txn = ethereum_client.w3.eth.account.signTransaction(dict(
        nonce=ethereum_client.w3.eth.getTransactionCount(local_account.address),
        gasPrice=ethereum_client.w3.eth.gasPrice,
        gas=200000,
        to=address_to,
        value=ethereum_client.w3.toWei(wei_amount, 'ether')
    ), HexBytes(local_account.privateKey).hex())

    tx_hash = ethereum_client.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    # Retrieve the tx_receipt
    tx_receipt = ethereum_client.get_transaction_receipt(tx_hash, timeout=60)
    return tx_receipt


def send_ether_to_safe(wei_amount, private_key):
    """ Send Ether To Safe
    This function will send ether to the address_to, wei_amount, private_key
    :param wei_amount:
    :param private_key:
    :return:
    """
    safe_address = ''
    send_ether_raw(safe_address, wei_amount, private_key)


def send_ether_from_safe(wei_amount, address_to):
    """ Send Ether To Safe
    This function will send ether to the address_to, wei_amount, private_key
    :param wei_amount:
    :param address_to:
    :return:
    """
    return

# def send_token():
#     return
# def deposit_token():
#     return
# def withdraw_token():
#     return


private_key = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
address_from = '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
address_to = '0xdAA71FBBA28C946258DD3d5FcC9001401f72270F'

balance_pre0 = ethereum_client.w3.eth.getBalance(address_from)
balance_pre1 = ethereum_client.w3.eth.getBalance(address_to)

send_ether_raw(address_to, 1, private_key)

balance0 = ethereum_client.w3.eth.getBalance(address_from)

balance1 = ethereum_client.w3.eth.getBalance(address_to)

print(balance_pre0, balance_pre1)
print(balance0, balance1)
# <>

new_value = balance_pre0 - balance0

current_value0 = balance_pre1 - balance1

print(new_value, current_value0)


balance_view = '{0:^40} [ {1:^40} ]'.format(balance0, new_value)
print('[ Address {0} New Balance ]:'.format(address_to), balance_view)
balance_view = '{0:^40} [ {1:^40} ]'.format(balance1, current_value0)
print('[ Address {0} New Balance ]:'.format(address_from), balance_view)

# Import Init Scenario ( To have a functional contract to test commands )
from safe_init_scenario_script import gnosis_py_init_tokens

gnosis_py_init_tokens()