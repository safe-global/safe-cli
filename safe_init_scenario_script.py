#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Contract Reader Module
from core.utils.contract_reader import ContractReader

# Import Ethereum Client Module
from gnosis.eth.ethereum_client import EthereumClient

# Import Safe, ProxyFactory Module
from gnosis.safe import Safe, ProxyFactory

# Import Account Module
from eth_account import Account

# Import Auto-Generated functions for retrieving instances of the Smart Contracts
from gnosis.eth.contracts import (
    get_safe_contract, get_safe_V1_0_0_contract, get_safe_V0_0_1_contract
)

from gnosis.eth.tests.utils import deploy_example_erc20

class AuxContractArtifact:
    def __init__(self, contract_name, contract_instance, contract_abi, contract_bytecode, contract_address):
        self.data = {
            'name': contract_name,
            'instance': contract_instance,
            'abi': contract_abi,
            'bytecode': contract_bytecode,
            'address': contract_address
        }

def gnosis_py_init_tokens(safe_address):
    # Get new Ethereum Provider
    contract_reader = ContractReader()
    ethereum_client = EthereumClient()
    token_abi, token_bytecode, token_name = contract_reader.read_from('./assets/contracts/ERC20TestToken.json')

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
    address_to = ''

    ethereum_client.erc20.send_tokens(safe_address, 15, token_address, private_key)
    token_balance = ethereum_client.erc20.get_balance(safe_address, erc20_contract.address)
    # print('safe_address', token_balance)

    user_for_testing = '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b'
    token_balance = ethereum_client.erc20.get_balance(user_for_testing, erc20_contract.address)
    # print('user_testing', token_balance)

    ethereum_client.erc20.send_tokens(user_for_testing, 10, token_address, private_key)
    token_balance = ethereum_client.erc20.get_balance(user_for_testing, erc20_contract.address)
    # print('user_testing', token_balance)

    user_for_testing_2 = '0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E'
    token_balance2 = ethereum_client.erc20.get_balance(user_for_testing_2, token_address)
    # print('other_testing', token_balance2)
    tx_hash = ethereum_client.erc20.send_tokens(user_for_testing_2, 12, token_address, private_key)
    token_balance2 = ethereum_client.erc20.get_balance(user_for_testing_2, token_address)
    # print('other_testing', token_balance2)
    # token_artifact = AuxContractArtifact(erc20_contract.functions.symbol().call(), erc20_contract, token_abi, token_bytecode, token_address)

    return token_address


def gnosis_py_init_scenario():
    # Get new Ethereum Provider & ContractReader
    ethereum_client = EthereumClient()
    contract_reader = ContractReader()

    # remark: Init Deployer Account
    local_account = Account.privateKeyToAccount('0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    safe_v101_abi, safe_v101_bytecode, safe_v101 = contract_reader.read_from(
        './assets/contracts/GnosisSafeV1.1.0.json')
    proxy_v101_abi, proxy_v101_bytecode, proxy_v101 = contract_reader.read_from(
        './assets/contracts/Proxy.json')

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
        ethereum_client.w3.eth.accounts[0], ethereum_client.w3.eth.accounts[1], ethereum_client.w3.eth.accounts[2]
    ]
    ethereum_tx_sent = Safe.create(
        ethereum_client, local_account, safe_v101_deployment_data.contract_address, owners,
        threshold, proxy_factory_address=proxy_v101_deployment_data.contract_address
    )
    safe_v101_object = Safe(ethereum_tx_sent.contract_address, ethereum_client)

    # remark: Start Retrieving Instance for the Contract
    safe_v101_contract_instance = get_safe_contract(ethereum_client.w3, safe_v101_object.address)
    print('| Successfully Retrieved', safe_v101, 'Contract Instance', safe_v101_contract_instance)

    # # remark: Test Commands For Each Safe Version 1.1.0
    # print('', '----------' * 14)
    # print('| Test (Name & Version):',
    #       safe_v101_contract_instance.functions.NAME().call(),
    #       safe_v101_contract_instance.functions.VERSION().call())
    # print('| Test (isOwner):',
    #       safe_v101_contract_instance.functions.isOwner(ethereum_client.w3.eth.accounts[0]).call())
    # print('| Test (getThreshold):', safe_v101_contract_instance.functions.getThreshold().call())
    # print('| Test (getOwners):', safe_v101_contract_instance.functions.getOwners().call())
    # print('', '----------' * 14)

    # remark: Setup Another Safe Account
    # local_account4 = Account.privateKeyToAccount('0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    # safe_owners_aux = [
    #     ethereum_client.w3.eth.accounts[4], ethereum_client.w3.eth.accounts[5],
    #     ethereum_client.w3.eth.accounts[6], ethereum_client.w3.eth.accounts[7],
    #     ethereum_client.w3.eth.accounts[8]
    # ]
    # safe_threshold_aux = 5
    # ethereum_tx_sent_aux = Safe.create(
    #     ethereum_client, local_account4, safe_v101_deployment_data.contract_address,
    #     safe_owners_aux, safe_threshold_aux, proxy_factory_address=proxy_v101_deployment_data.contract_address
    # )
    # safe_v101_object_0 = Safe(ethereum_tx_sent_aux.contract_address, ethereum_client)
    # print('| loadSafe --address=%s ' % (ethereum_tx_sent_aux.contract_address))
    # print('| loadContract --alias=%s ' % (safe_v101))
    # print('', '----------' * 14)

    # safe_v101_artifacts = AuxContractArtifact(
    #     safe_v101, safe_v101_contract_instance, safe_v101_abi, safe_v101_bytecode, safe_v101_object.address
    # )
    return safe_v101_object.address #[safe_v101_artifacts.data]
