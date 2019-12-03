#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

from enum import Enum

from core.artifacts.token_artifacts import TokenArtifacts
from core.artifacts.data_artifacts import DataArtifacts

# wei = int(units["wei"])
# kwei = int(units["kwei"])
# babbage = int(units["babbage"])
# femtoether = int(units["femtoether"])
# mwei = int(units["mwei"])
# lovelace = int(units["lovelace"])
# picoether = int(units["picoether"])
# gwei = int(units["gwei"])
# shannon = int(units["shannon"])
# nanoether = int(units["nanoether"])
# nano = int(units["nano"])
# szabo = int(units["szabo"])
# microether = int(units["microether"])
# micro = int(units["micro"])
# finney = int(units["finney"])
# milliether = int(units["milliether"])
# milli = int(units["milli"])
# ether = int(units["ether"])
# kether = int(units["kether"])
# grand = int(units["grand"])
# mether = int(units["mether"])
# gether = int(units["gether"])
# tether = int(units["tether"])
# KWei = 1000000000000000
# MWei = 1000000000000
# GWei = 1000000000
# Shannon = 1000000000
# Szabo = 1000000
# Finney = 1000
# Ether = 1
# KEther = 0.001
# MEther = 0.000001
# GEther = 0.000000001
#
# '--wei'
# '--kwei'
# '--babbage'
# '--mwei'
# '--lovelace'
# '--picoether'
# '--gwei'
# '--shannon'
# '--nanoether'
# '--szabo'
# '--microether'
# '--micro'
# '--finney'
# '--milliether'
# '--milli'
# '--ether'
# '--kether'
# '--grand'
# '--mether'
# '--gether'
# '--tether'
#




from core.input.console_input_getter import ConsoleInputGetter
from gnosis.eth.ethereum_client import EthereumClient
ethereum_client = EthereumClient()

# If you use deimcal, you need to import
from decimal import getcontext, Decimal

# <>
class EtherHelper:
    def __init__(self, logger, ethereum_client):
        self.name = self.__class__.__name__
        self.logger = logger
        self.ethereum_client = ethereum_client

    def get_proper_ether_amount(self, ether_amount):
        k_ether = self.ethereum_client.w3.toWei(1, 'kether')
        m_ether = self.ethereum_client.w3.toWei(1, 'mether')
        g_ether = self.ethereum_client.w3.toWei(1, 'gether')
        t_ether = self.ethereum_client.w3.toWei(1, 'tether')

        if ether_amount >= t_ether:
            return 'T-Ether', self.ethereum_client.w3.fromWei(ether_amount, 'tether')
        elif ether_amount >= g_ether:
            return 'G-Ether', self.ethereum_client.w3.fromWei(ether_amount, 'gether')
        elif ether_amount >= m_ether:
            return 'M-Ether', self.ethereum_client.w3.fromWei(ether_amount, 'mether')
        elif ether_amount >= k_ether:
            return 'K-Ether', self.ethereum_client.w3.fromWei(ether_amount, 'kether')
        else:
            return 'Ether', ether_amount

    def unify_ether_badge_amounts(self, ether_badge, ether_amounts):
        """"""
        ether_amount = 0
        if ether_amounts:
            self.logger.debug0('[ Badge Id ]: {0:^14} | {1}'.format(ether_badge, ether_amounts))
            for ether_badge_amount in ether_amounts:
                if ether_badge == '--wei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'wei')
                elif ether_badge == '--kwei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'kwei')
                elif ether_badge == '--babbage':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'babbage')
                elif ether_badge == '--mwei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'mwei')
                elif ether_badge == '--lovelace':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'lovelace')
                elif ether_badge == '--picoether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'picoether')
                elif ether_badge == '--gwei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'gwei')
                elif ether_badge == '--shannon':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'shannon')
                elif ether_badge == '--nanoether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'nanoether')
                elif ether_badge == '--szabo':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'szabo')
                elif ether_badge == '--microether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'microether')
                elif ether_badge == '--micro':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'micro')
                elif ether_badge == '--finney':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'finney')
                elif ether_badge == '--milliether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'milliether')
                elif ether_badge == '--milli':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'milli')
                elif ether_badge == '--ether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'ether')
                elif ether_badge == '--kether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'kether')
                elif ether_badge == '--grand':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'grand')
                elif ether_badge == '--mether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'kether')
                elif ether_badge == '--gether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'gether')
            return ether_amount
        return ether_amount

    def get_unify_ether_amount(self, ether_badge_parsed_list):
        final_amount = 0
        for item_data in ether_badge_parsed_list:
            final_amount += self.unify_ether_badge_amounts(item_data[0], item_data[1])
        self.logger.debug0('{0}'.format(ethereum_client.w3.fromWei(final_amount, 'ether')))
        return final_amount
        # ethereum_client.w3.fromWei(final_amount, 'ether')


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

logger.addHandler(console_handler)
console_getter = ConsoleInputGetter(logger)
ether_helper = EtherHelper(logger, ethereum_client)

desired_parsed_item_list, _, _, _ = console_getter.get_gnosis_input_command_argument(send_ether_amount)
final_amount = ether_helper.get_unify_ether_amount(desired_parsed_item_list[1:])
print(ether_helper.get_proper_ether_amount(final_amount))

