def _setup_console_contract_configuration(self, configuration):
    """ Setup Console Contract Configuration
    This function will load contract_cli eth_assets for the console to have access to
    :param configuration:
    :return:
    """
    if configuration['abi'] and configuration['contract_cli']:
        self.logger.debug0(configuration['contract_cli'])
        self.logger.debug0(configuration['abi'])

        for contract_index, contract_abi in enumerate(configuration['abi']):
            contract_address = configuration['contract_cli'][contract_index]
            contract_abi, contract_bytecode, contract_name = self.contract_reader.read_from(contract_abi)

            contract_instance = self.network_agent.ethereum_client.w3.eth.contract(
                abi=contract_abi, address=contract_address)

            self.contract_artifacts.add_contract_artifact(
                contract_name, contract_instance, contract_abi, contract_bytecode, contract_address, contract_name)

    elif configuration['abi'] and not configuration['contract_cli']:
        for contract_abi in configuration['abi']:
            contract_abi, contract_bytecode, contract_name = self.contract_reader.read_from(contract_abi)
            self.contract_artifacts.add_contract_artifact(
                contract_name, None, contract_abi, contract_bytecode, None, contract_name)


def run_contract_console(self, contract_alias):
    """ Run Contract Console
    This function will run the contract_cli console
    :param contract_alias:
    :return:
    """
    try:
        self.log_formatter.log_entry_message('Entering Contract Console')
        set_title('Contract Console')
        self.contract_interface = self.data_artifacts.retrive_from_stored_values(
            contract_alias, 'instance', 'contract_cli')
        self.logger.debug0('Contract Instance {0} Loaded'.format(self.contract_interface))
        self.contract_methods = ConsoleContractCommands().map_contract_methods(self.contract_interface)
        self.active_session = TypeOfConsole.CONTRACT_CONSOLE
        self.run(
            prompt_text=self._get_prompt_text(affix_stream='contract_cli-cli', stream=contract_alias))
    except KeyError as err:
        self.logger.error(err)