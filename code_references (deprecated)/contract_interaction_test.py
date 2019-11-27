#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from core.constants.contract_contants import NULL_ADDRESS

# Import GnosisSafe Module
from core.utils.gnosis_safe_setup import GnosisSafeModule

# Import Provider Packages
from core.utils.provider.ganache_provider import GanacheProvider

# Import Contract Interface
from core.console_truffle_interface import ConsoleTruffleInterface

# Import Prompt Toolkit Packages
from core.console_engine import GnosisConsoleEngine
from prompt_toolkit.completion import WordCompleter
import os

# Import Eth Account Package
from eth_account import Account

# Import Transaction History Manager Package

# Import Gnosis CLI

# Todo: This should be moved to the ganache_provider.
# Import default deterministic account information for Ganache Provider
from core.constants.ganache_constants import DETERMINISTIC_ACCOUNT_INFORMATION

PROJECT_DIRECTORY = os.getcwd() + '/assets/safe-contracts-1.1.0/'
CONTRACT_SOL_DIRECTORY = PROJECT_DIRECTORY + 'contracts/'
CONTRACT_BUILD_DIRECTORY = PROJECT_DIRECTORY + 'build/contracts/'

gnosis_safe_cli_completer = [
    'safe_addr', 'add', 'after', 'all', 'before', 'check',
    'current_date', 'current_time', 'current_timestamp', 'current_block'
    'default', 'delete', 'exit', 'quit', 'without',
]

# Todo: Finish the multi sign Transaction for the proxy contract.
# note: The contracts will be compiled via subprocess using truffle compile this is maily because the current versions
#  for py-solcx and py-sol reports an error while trying to access the mock contracts in GnosisSafe Project.

# Import Web3

def call_gnosis_console(contract_instance):
    print('Launching Gnosis Console')
    gnosis_cli = GnosisConsoleEngine(contract_instance)
    gnosis_cli.run_console_session(WordCompleter(gnosis_safe_cli_completer, ignore_case=True))

# Todo: to be moved to AccountManager?
def retrieve_default_accounts():
    """ Retrieve Default Ganache Accounts,
    This function will recover and return the default accounts created with the -d deterministic param, in a sorted list
    using de private_key as starting point.
    :return: Sorted List[Account Instance]
    """
    account_list = []
    for account in DETERMINISTIC_ACCOUNT_INFORMATION:
        account_list.append(Account.from_key(DETERMINISTIC_ACCOUNT_INFORMATION[account]['private_key']))
    sorted_accounts = sorted(account_list, key=lambda item: item.address.lower())
    return sorted_accounts


def multi_sign_tx(signers, tx_hash):
    """

    :param self:
    :param signers:
    :param tx_hash:
    :return:
    """

    very_important_data = [Account.from_key(signers[0]), Account.from_key(signers[1])]
    print('Input signers', signers)
    # generar Account y ordenar por address.

    orderred_signers = sorted(very_important_data, key=lambda v: v.address.lower())
    print('Ordered Signers', orderred_signers)
    signature_bytes = b''
    for private_key in signers:
        tx_signature = Account.signHash(tx_hash, private_key)
        signature_bytes += tx_signature['signature']

    print('[ Output Signature ]: ' + signature_bytes.hex())
    return signature_bytes

# 0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000
# 0x519ac607c6c6a7efc4875850dd94ed8481b640690970f5cd7b6f131f3ef0f5450x23f57809a0938c7c61e4ebad27d7bc2580c5ac5592dd9086e6e478d5db2fbed10x000000000000000000000000000000000000000000000000000000000000001b0x55e191536a3a87340489f6b49839411bc8d253503d309c3fab1aaf3e9d1a64180x2f5bad903e2db05329f45b756e13c7a7db839937bef0f5f02c71802254a3cc510x000000000000000000000000000000000000000000000000000000000000001c
# tx_history = TransactionHistoryManager()
def gnosis_test():
    # Set Ganache Provider
    ganache_provider = GanacheProvider()
    provider = ganache_provider.get_provider()
    # remark: Link to the current contracts via ABI + Bytecode
    contract_interface = ConsoleTruffleInterface(provider, PROJECT_DIRECTORY, ['GnosisSafe'], ['Proxy'])
    # deploy_contract() will call compile_source_files() if the contract is not yet compiled.
    contract_interface.compile_source_files()
    contract_artifacts = contract_interface.deploy_contract()

    # remark: Get Contract Artifacts for the Proxy & GnosisSafe
    safe_instance = contract_interface.get_new_instance(contract_artifacts['GnosisSafe'])
    proxy_instance = contract_interface.get_new_instance(contract_artifacts['Proxy'])

    # remark: Get Interface to interact with the contract
    gnosis_safe_module = GnosisSafeModule(provider, contract_artifacts)
    functional_safe = gnosis_safe_module.setup(safe_instance, proxy_instance)

    # remark: hardcoded private keys for ganache provider
    private_key_account0 = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    private_key_account1 = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    private_key_account2 = '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
    # remark: get Account instances from every private key
    users_to_sign = [Account.from_key(private_key_account0), Account.from_key(private_key_account1), Account.from_key(private_key_account2)]
    print('[ Accounts ]:', users_to_sign)
    orderred_signers = sorted(users_to_sign, key=lambda v: v.address.lower())
    print(orderred_signers[0].address, 'is Owner?', functional_safe.functions.isOwner(orderred_signers[0].address).call())
    print(orderred_signers[1].address, 'is Owner?', functional_safe.functions.isOwner(orderred_signers[1].address).call())
    print(orderred_signers[2].address, 'is Owner?', functional_safe.functions.isOwner(orderred_signers[2].address).call())

    # remark: Data to ve used in the Transaction
    new_account_to_add = Account.create()
    new_account_address = new_account_to_add.address
    base_gas = 200000
    safe_tx_gas = 300000
    gas_price = 0
    nonce = functional_safe.functions.nonce().call()
    current_owners = functional_safe.functions.getOwners().call()
    CALL = 0
    proxy_address = contract_artifacts['Proxy']['address']

    # remark: Generate transaction for the addOwnerWithThreshold
    print('\nCurrent Owners of the Safe:\n', current_owners)
    # transaction = functional_safe.functions.addOwnerWithThreshold(new_account_address, 3).buildTransaction({'from': orderred_signers[0].address})
    transaction = functional_safe.functions.changeThreshold(3).buildTransaction({'from': proxy_address})
    # transaction.update({'nonce': nonce, 'gasPrice': 1})
    print('Current Transaction: \n', transaction['data'])

    # remark: Since we need the Hash for the fucntion to be signed, with the gas data from before we create the
    #  new transaction data: payload of the new transaction
    tx_change_threshold = functional_safe.functions.getTransactionHash(
        proxy_address, 0, transaction['data'], 0, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, nonce
    ).call()

    # remark: Sign Transaction Hash
    signature_bytes = b''
    for signers in orderred_signers[1:]:
        tx_signature = signers.signHash(tx_change_threshold)
        signature_bytes += tx_signature['signature']
    print('[ Output Signature ]: ' + signature_bytes.hex())

    try:
        # remark: Launch the current transaction usign execTransaction
        change_treshold_hash = functional_safe.functions.execTransaction(
            proxy_address, 0, transaction['data'], 0, safe_tx_gas, base_gas, gas_price, NULL_ADDRESS, NULL_ADDRESS, signature_bytes
        ).transact({'from': orderred_signers[0].address, 'gas': safe_tx_gas + base_gas})

        # remark: KEEP WAITING FOR THE TRANSACTION TO BE MINED¡
        receipt_for_change_threshold = provider.eth.waitForTransactionReceipt(change_treshold_hash)
        print('\n', receipt_for_change_threshold)
    except Exception as err:
        print(err)
    current_owners = functional_safe.functions.getThreshold().call()
    print('\nCurrent Owners of the Safe:\n', current_owners)

    # myfilter_success = proxy_instance.eventFilter('ExecutionSuccess', {'fromBlock': 0, 'toBlock': 'latest'});
    # myfilter_failure = proxy_instance.eventFilter('ExecutionFailure', {'fromBlock': 0, 'toBlock': 'latest'});
    # eventlist_failure = myfilter_failure.get_all_entries()
    # eventlist_success = myfilter_success.get_all_entries()

    # print('++++++++++++++'*10)
    # print('failure:\n', eventlist_failure)
    # print('success:\n', eventlist_success)
    call_gnosis_console(functional_safe)


def main():
    gnosis_test()


if __name__ == '__main__':
    main()

# note:
# python click_test.py --network=ganache --pkey --silence --debug
# (gnosis-safe-cli)>:
# (gnosis-safe-cli)>: viewNetwork
# (gnosis-safe-cli)>: setNework --name=ganache
# (gnosis-safe-cli)>: setNework --id=0
# (gnosis-safe-cli)>:
# (gnosis-safe-cli)>: viewAccount
# (gnosis-safe-cli)>: newAccount --address= --pkey=|--mnemonic=
# (gnosis-safe-cli)>:
# (gnosis-safe-cli)>: loadContract --address=0x(0)*40 --abi=/path/to/abi/
# (gnosis-safe-cli)>: loadContract --build=/path/to/build/
# (gnosis-safe-cli)>:
# (gnosis-safe-cli)>: viewSession
# (gnosis-safe-cli)>: loadSession --alias=Gnosis_Safe_v1.1.0
# (gnosis-safe-cli)>: loadSession --index=1
# (gnosis-safe-cli)>: setDefaultSession --alias=Gnosis_Safe_v1.1.0
# (gnosis-safe-cli)>: setDefaultSession --index=1

# (gnosis-safe-cli)
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>:
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: getOwners --query
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>:
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: getThreshold --query
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>:
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: changeThreshold --uint=8 --address=0x(0*40) --address=0x(0*40) --execute|--queue

# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: view gas
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>:
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: setGasLimit 0
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: setSafeGas 0
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: setGas 0

# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: view txReceipts
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: view txHistory
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: view batch

# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: view owners
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>:
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: setDefaultOwner 0x(0*40)
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: setDefaultOwnerList 0x(0*40) 0x(0*40) 0x(0*40)
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>:
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: runSetup
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: newSetup
# [ ./newSetup ][ Gnosis-Safe(v1.1.0) ]>:
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: newPayload
# [ ./newPayload ][ Gnosis-Safe(v1.1.0) ]>: --address=
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: newCustom
# [ ./newCustom ][ Gnosis-Safe(v1.1.0) ]>: payload --address=
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>: close/exit/quit
# [ ./ ][ Gnosis-Safe(v1.1.0) ]>:
