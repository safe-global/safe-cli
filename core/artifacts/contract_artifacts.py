#!/usr/bin/env python3
# -*- coding: utf-8 -*-

STRING_DASHES = '----------' * 12


class ContractArtifacts:
    def __init__(self, logger):
        self.logger = logger
        self.contract_data = {}

    def pre_load_artifacts(self, contract_artifacts):
        if contract_artifacts is not None:
            self.logger.debug0('')
            self.logger.debug0(' | Setup Contract Artifacts  | ')
            self.logger.debug0(STRING_DASHES)
            for artifact in contract_artifacts:
                self.logger.debug0('(+) Contract Artifact [ {0} with Address {1} ]'.format(
                    artifact['name'], artifact['address'])
                )
                self.add_contract_artifact(
                    artifact['name'], artifact['instance'], artifact['abi'],
                    artifact['bytecode'], artifact['address'], (artifact['name'] + '_' + str(len(self.contract_data)))
                )

    def command_view_contracts(self):
        """ Command View Contracts

        :return:
        """
        abi_status = False
        bytecode_status = False

        self.logger.debug0(STRING_DASHES)
        for artifact_identifier in self.contract_data:
            # Temporary fix for showing ( True | False ) that the abi & bytecode are present
            if len(self.contract_data[artifact_identifier]['abi']) > 1:
                abi_status = True
            if len(self.contract_data[artifact_identifier]['bytecode']) > 1:
                bytecode_status = True

            self.logger.info(' | {0:^25} | {1:^25} | {2:^25} | {3:^10} | {4:^10} | '.format(
                str(artifact_identifier), str(self.contract_data[artifact_identifier]['name']),
                str(self.contract_data[artifact_identifier]['address']), str(abi_status),
                str(bytecode_status))
            )
        self.logger.debug0(STRING_DASHES)

    def new_contract_entry(self, contract_name, contract_instance, contract_abi, contract_bytecode, contract_address):
        return {
            'name': contract_name, 'instance': contract_instance, 'abi': contract_abi,
            'bytecode': contract_bytecode, 'address': contract_address
        }

    def add_contract_artifact(self, contract_name, contract_instance, contract_abi, contract_bytecode, contract_address, alias=''):
        """ Add Artifacts

        :param contract_name:
        :param contract_instance:
        :param contract_abi:
        :param contract_bytecode:
        :param contract_address:
        :param alias:
        :return:
        """
        if alias != '':
            self.contract_data[str(alias)] = self.new_contract_entry(contract_name, contract_instance, contract_abi, contract_bytecode, contract_address)
        else:
            self.contract_data[str(contract_name)] = self.new_contract_entry(
                contract_name, contract_instance, contract_abi, contract_bytecode, contract_address
            )
