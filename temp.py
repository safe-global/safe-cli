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

from gnosis.eth.ethereum_client import EthereumClient
ethereum_client = EthereumClient()

# If you use deimcal, you need to import
from decimal import getcontext, Decimal

# Set the precision.
getcontext().prec = 3

# Execute 1/7, however cast both numbers as decimals
output = Decimal(16000000000000000.0)/Decimal(7)

# Your output will return w/ 6 decimal places, which
# we set above.
print(output)

# <>
def get_proper_ether_amount(ether_amount):
    k_ether = 1000
    m_ether = 1000000
    g_ether = 1000000000
    t_ether = 1000000000000

    if ether_amount >= t_ether:
        return 'T-Ether', ethereum_client.w3.fromWei(ether_amount, 'tether')
    elif ether_amount >= g_ether:
        return 'G-Ether', ethereum_client.w3.fromWei(ether_amount, 'gether')
    elif ether_amount >= m_ether:
        return 'M-Ether', ethereum_client.w3.fromWei(ether_amount, 'mether')
    elif ether_amount >= k_ether:
        return 'K-Ether', ethereum_client.w3.fromWei(ether_amount, 'kether')
    else:
        return 'Ether', ether_amount

def unify_ether_badge_amounts(argument_list):
    ether_amount = 0
    for item in argument_list:
        if item.startswith('--wei='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'wei')
        if item.startswith('--kwei='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'kwei')
        if item.startswith('--mwei='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'mwei')
        if item.startswith('--gwei='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'gwei')
        if item.startswith('--shannon='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'shannon')
        if item.startswith('--szabo='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'szabo')
        if item.startswith('--finney='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'finney')
        if item.startswith('--ether='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'ether')
        if item.startswith('--kether='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'kether')
        if item.startswith('--mether='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'kether')
        if item.startswith('--gether='):
            value = 0
            ether_amount += ethereum_client.w3.toWei(value, 'gether')

        return ethereum_client.w3.fromWei(ether_amount, 'ether')

# sum_output = unify_ether_badge_amounts([0.00000000001, 0.10, 1, 10])

# print(0.000000001 * g_ether)

print(get_proper_ether_amount(1000000000001))
print(get_proper_ether_amount(10))
print(get_proper_ether_amount(100000022))

ethereum_client.w3.fromWei(10, 'ether')


