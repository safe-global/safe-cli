from core.utils.gnosis_safe_setup import GnosisSafeModule
from core.console_truffle_interface import ConsoleTruffleInterface
from core.utils.provider.ganache_provider import GanacheProvider
import os

def truffle_init_scenario():
    print('---------' * 10)
    print('Init of the Contract Scenario')
    print('---------' * 10)
    PROJECT_DIRECTORY = os.getcwd() + '/assets/safe-contracts-1.1.0/'
    ganache_provider = GanacheProvider()

    provider = ganache_provider.get_provider()
    contract_interface = ConsoleTruffleInterface(provider, PROJECT_DIRECTORY, ['GnosisSafe'], ['Proxy'])
    contract_artifacts = contract_interface.deploy_contract()

    # remark: Get Contract Artifacts for the Proxy & GnosisSafe
    safe_instance = contract_interface.get_new_instance(contract_artifacts['GnosisSafe'])
    proxy_instance = contract_interface.get_new_instance(contract_artifacts['Proxy'])

    # remark: Get Interface to interact with the contract
    gnosis_safe_module = GnosisSafeModule(provider, contract_artifacts)
    functional_safe = gnosis_safe_module.setup(safe_instance, proxy_instance)

    print('---------' * 10)
    tmp_contract_artifacts = {
        'instance': functional_safe,
        'abi': contract_artifacts['GnosisSafe']['abi'],
        'bytecode': contract_artifacts['GnosisSafe']['bytecode'],
        'address': contract_artifacts['GnosisSafe']['address']
    }

    return tmp_contract_artifacts