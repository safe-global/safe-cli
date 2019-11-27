#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Todo: Lexer per init of console, type of session, so emun to flag the type focusing on usability in the future
# Todo: Module loader, so it can run the setup for the contract you want to operate with
# Todo: Report the pos of the word to the lexer so it can know if it's dealing with a call to a function or an param
# Todo: Build the suffix + affix list for the management of simple contracts
# Todo: Improve function mapping so it can properly separate Events(Emit's) from the contract methods from the actual functions
# Todo: Maybe Add a listener for the Events done by the contract atleast locally so it can be studied how it behaves
# Todo: Add Interface for the Common Contract Operations Setup(), Transact() etc etc so it can be called from the console
#   If None are provided, the console will assume an standar way of operation for the basic known transaction procedures
# Todo: Move Current "Setup" for the GnosisSafe to it's proper module
# Todo: Move Current "Transact" overrider to the GnosisSafe module
# Todo: Only add to the temporal lexer valid addresses (it has been operated with)

# validator = Validator.from_callable(
#     is_valid_address, error_message='Not a valid address (Does not contain an 0x).', move_cursor_to_end=True
# )

query_is_owner = 'isOwner --address=0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 --query'
execute_swap_owner = 'swapOwner --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002 --from=0x00000000000000000000000000000003 --execute'
query_get_owners = 'getOwners --query'
query_execTransaction_not_enough_args = 'execTransaction --queue --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002'


# # remark: transact with arguments
# # note: could be autofilled if not provided and set in the console session
# #
#
# # kwown arguments gas:, gasPrices:, nonce:, from:
#
# #     # nonce = functional_safe.functions.nonce().call()
# #     # transaction = functional_safe.functions.changeThreshold(3).buildTransaction({'from': orderred_signers[0].address})
# #     # transaction.update({'gas': base_gas})
# #     # transaction.update({'gasPrice': gas_price})
# #     # transaction.update({'nonce': nonce})
#
# # note: --from=, --gas=, nonce=, gasprice=
#
# import re
#
# def is_alphanumeric_addres(stream):
#     data = re.search(r'^(0x)?[0-9a-f]{40}$', stream).group(0)
#     print('data', data)
#     return
#
# # def validated(stream):
# #     # remark: evaluate the data been passed to the contracts by searching it's current value,key
# #     if is_alphanumeric_addres(stream):
# #         return
# #     return
#
# is_valid_address = r'^(0x)?[0-9a-f]{40}$'
# is_62_valid_address = r'^(0x)?[0-9a-f]{62}$'
#
# def print_kwargs(**kwargs):
#     new_values = ''
#     for key, value in kwargs.items():
#         if key.strip('_') in ['from', 'gas']: # and validated(key, value):
#             new_values += '\'{0}\':{1},'.format(key.strip('_'), value)
#             print(new_values)
#     return new_values
#
# aux = print_kwargs(_from="Shark", gas=4.5)
#
# data_to_print = 'data_to_be_printed.transact{%s}' % (aux[:-1])
# print(data_to_print)
#
# from ethereum import utils
#
# def checksum_encode(addr): # Takes a 20-byte binary address as input
#     o = ''
#     v = utils.big_endian_to_int(utils.sha3(addr.hex()))
#     for i, c in enumerate(addr.hex()):
#         if c in '0123456789':
#             o += c
#         else:
#             o += c.upper() if (v & (2**(255 - 4*i))) else c.lower()
#         print(o)
#     return '0x'+o
#
# def some_args(arg_1, arg_2, arg_3):
#     print("arg_1:", arg_1)
#     print("arg_2:", arg_2)
#     print("arg_3:", arg_3)
#
# my_list = [2, 3]
# some_args(1, *my_list)
#
# # Doble input:
# # for i in range(0, n):
# #     ele = [input(), int(input())]
#
# # https://ethereum.stackexchange.com/questions/1374/how-can-i-check-if-an-ethereum-address-is-valid
# # ^(0x)?[0-9a-f]{40}$
# # https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md#implementation
#
# from hexbytes import HexBytes
# from web3 import Web3
#
# def test(addrstr):
#     assert(addrstr == Web3.toChecksumAddress(addrstr))
#
# print(Web3.toChecksumAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed'))
# print(Web3.toChecksumAddress('0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359'))
# print(Web3.toChecksumAddress('0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB'))
# print(Web3.toChecksumAddress('0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb'))
#
# from web3 import Web3
# execute = True
#
# # Currency Utility
# # Gather all the --Gwei, --Kwei etc etc sum up them and give the ''
# if execute:
#     Web3.fromWei(1000000000000000000, 'Gwei')
# #Web3.toWei()
# #Web3.fromWei()
#
# # Address Utility
# Web3.isAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
# Web3.isChecksumAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
