#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import Enum Module
from enum import Enum

class TypeOfAccount(Enum):
    """ Type Of Account
    Enum defining known types of accounts
    """
    LOCAL_ACCOUNT = 'Local_Account'
    RINKEBY_ACCOUNT = 'Rinkeby_Account'
    MAINNET_ACCOUNT = 'Mainnet_Account'
    ROPSTEN_ACCOUNT = 'Ropsten_Account'

class TypeOfPayload(Enum):
    """ Type Of Payload
    Enum defining known type of Payload
    """
    SENDER_PAYLOAD = '{}'
    TX_PAYLOAD = '{}'


class TypeOfTokens(Enum):
    """ Type Of Tokens
    Enum defining known types of Token
    """
    ERC20 = 'ERC20'
    ERC721 = 'ERC721'
