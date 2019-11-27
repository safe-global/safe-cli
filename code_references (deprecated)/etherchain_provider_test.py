#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyetherchain.pyetherchain import EtherChain

e = EtherChain()

# getting an accoutn object
ac = e.account("0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef")

# show the account object (json), retrieve the source if available, show transactions
print(ac)
print(ac.source)
print(ac.swarm_hash)
print(ac.transactions())
print(ac.history())
# access the charts api
print(e.charts.market_cap())
# retrieve hardfork information
print(e.hardforks())


# list pending transaactions (takes arguments)
# print(e.transactions_pending())
# describe the constructor invokation and other transaction in a human readable way
contract = e.account("0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef")
# print("constructor:{}".format(contract.abi.describe_constructor(contract.constructor_args)))
# for tx in contract.transactions(direction="in", length=10000)["data"]:
#     tx_obj = e.transaction(tx["parenthash"])[0]
#     print("transaction: [IN] <== %s : %s".format((str(tx_obj["hash"]), str(contract.abi.describe_input(tx_obj["input"])))))

# or just shorthand dump contract with extra info
contract.describe_contract()

# directly work with the backend api interface

# print(e.get_transaction("c98061e6e1c9a293f57d59d53f4e171bb62afe3e5b6264e9a770406a81fb1f07"))
# print(e.get_transactions_pending())
# print(e.get_transactions())
# print(e.get_blocks())
# print(e.get_accounts())
# print(e.get_hardforks())
#
# # print e.get_correlations()
# # print e.get_stats_price_btc()
# print(e.get_account_transactions("0x1104e154efa21ff3ca5da097f8906cd56b1e7d86"))

try:
    print(e.get_account_abi("0x1104e154efa21ff3ca5da097f8906cd56b1e7d86"))
    print(e.get_account_source(("0x1104e154efa21ff3ca5da097f8906cd56b1e7d86")))

except Exception as e:
    pass