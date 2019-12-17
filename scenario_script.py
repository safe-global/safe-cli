#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Contract Reader Module
from core.eth_assets.helper.contract_reader import ContractReader

# Import Ethereum Client Module
from gnosis.eth.ethereum_client import EthereumClient

# Import Safe, ProxyFactory Module
from gnosis.safe import Safe, ProxyFactory

# Import Account Module
from eth_account import Account

# Import Auto-Generated functions for retrieving instances of the Smart Contracts
from gnosis.eth.tests.utils import deploy_example_erc20


def deploy_uxi_tokens(safe_address):
    # Get new Ethereum Provider
    ethereum_client = EthereumClient()

    account0 = ethereum_client.w3.eth.accounts[0]
    erc20_contract = deploy_example_erc20(ethereum_client.w3, 100, account0)
    token_address = erc20_contract.address
    print('', '----------' * 14)
    print('| Contract Address for Token {0}: {1}'.format(
        erc20_contract.functions.symbol().call(), erc20_contract.address)
    )
    print('', '----------' * 14)
    token_balance = ethereum_client.erc20.get_balance(safe_address, erc20_contract.address)
    private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    print('safe_address', token_balance)

    ethereum_client.erc20.send_tokens(safe_address, 15, token_address, private_key)
    token_balance = ethereum_client.erc20.get_balance(safe_address, erc20_contract.address)
    print('safe_address', token_balance)

    user_for_testing = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    token_balance = ethereum_client.erc20.get_balance(user_for_testing, erc20_contract.address)
    print('user_testing', token_balance)

    ethereum_client.erc20.send_tokens(user_for_testing, 10, token_address, private_key)
    token_balance = ethereum_client.erc20.get_balance(user_for_testing, erc20_contract.address)
    print('user_testing', token_balance)

    print('Token_Address:', token_address)
    return token_address


def deploy_gnosis_safe_v1_1_1():
    # Get new Ethereum Provider & ContractReader
    ethereum_client = EthereumClient()
    contract_reader = ContractReader()

    local_account = Account.privateKeyToAccount('0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    safe_v111_abi, safe_v111_bytecode, safe_v111 = contract_reader.read_from(
        './assets/contracts/GnosisSafeV1.1.1.json')

    safe_v111_deployment_data = Safe.deploy_master_contract(ethereum_client, local_account)
    print('| Successfully Deployed', safe_v111, 'with Address:', safe_v111_deployment_data.contract_address)
    print('', '----------' * 14)

    print('Safe_Address_V1.1.1:', safe_v111_deployment_data.contract_address)
    return safe_v111_deployment_data.contract_address


def deploy_gnosis_safe_v1_1_0():
    # Get new Ethereum Provider & ContractReader
    ethereum_client = EthereumClient()
    contract_reader = ContractReader()

    # remark: Init Deployer Account
    local_account = Account.privateKeyToAccount('0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    safe_v101_abi, safe_v101_bytecode, safe_v101 = contract_reader.read_from('./assets/contracts/GnosisSafeV1.1.0.json')
    proxy_v101_abi, proxy_v101_bytecode, proxy_v101 = contract_reader.read_from('./assets/contracts/Proxy.json')

    # remark: Start Safe Contract Deployment
    print('', '----------' * 14)
    proxy_v101_deployment_data = ProxyFactory.deploy_proxy_factory_contract(ethereum_client, local_account)
    print('| Successfully Deployed', proxy_v101, 'with Address:', proxy_v101_deployment_data.contract_address)
    # remark: Start Safe Contract Deployment
    safe_v101_deployment_data = Safe.deploy_master_contract(ethereum_client, local_account)
    print('| Successfully Deployed', safe_v101, 'with Address:', safe_v101_deployment_data.contract_address)
    print('', '----------' * 14)

    # remark: Setup for the Safe Contract
    threshold = 1
    owners = [
        ethereum_client.w3.eth.accounts[0]
    ]
    ethereum_tx_sent = Safe.create(
        ethereum_client, local_account, safe_v101_deployment_data.contract_address, owners,
        threshold, proxy_factory_address=proxy_v101_deployment_data.contract_address
    )
    safe_v101_object = Safe(ethereum_tx_sent.contract_address, ethereum_client)

    print('Safe_AddressV1.0.1:', safe_v101_object.address)
    return safe_v101_object.address


safe_address = deploy_gnosis_safe_v1_1_0()
token_address = deploy_uxi_tokens(safe_address)
new_safe_address = deploy_gnosis_safe_v1_1_1()
