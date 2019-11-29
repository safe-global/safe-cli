#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# number_of_elements = [([*aux_value_retainer.keys()][index], item, len(item)) for index, item in enumerate(aux_value_retainer.values())]

# Todo: Maybe Add a listener for the Events done by the contract atleast locally so it can be studied how it behaves
# Todo: Only add to the temporal lexer valid addresses (it has been operated with)
# reference: https://ethereum.stackexchange.com/questions/1374/how-can-i-check-if-an-ethereum-address-is-valid
# reference: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md#implementation

query_execTransaction_not_enough_args = 'execTransaction --queue --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002'
execute_swap_owner = 'swapOwner --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002 --from=0x00000000000000000000000000000003 --execute'
query_is_owner = 'isOwner --address=0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 --query'
query_get_owners = 'getOwners --query'

# is_valid_address = r'^(0x)?[0-9a-f]{40}$'
# is_62_valid_address = r'^(0x)?[0-9a-f]{62}$'
# Currency Utility
# Web3.fromWei(1000000000000000000, 'Gwei')
# Address Utility
# Web3.isAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
# Web3.isChecksumAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
