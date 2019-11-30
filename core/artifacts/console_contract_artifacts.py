#!/usr/bin/env python3
# -*- coding: utf-8 -*-

STRING_DASHES = '---------' * 10


class ConsoleContractArtifacts:
    def __init__(self, contract_artifact_list=None):
        self.contract_artifact_list = contract_artifact_list
        self.contract_data = {}

    def command_view_contracts(self):
        """ Command View Contracts

        :return:
        """
        for item in self.contract_data:
            print(item, self.contract_data[item]['address'],
                  self.contract_data[item]['instance'])

    def add_artifact(self, contract_artifacts, alias=''):
        """ Add Artifacts

        :param contract_artifacts:
        :param alias:
        :return:
        """
        if alias != '':
            self.contract_data[alias] = contract_artifacts
            return self.contract_data

        self.contract_data['uContract' + str(len(self.contract_data))] = contract_artifacts

        return self.contract_data

    def get_value_from_alias(self, alias, key=None):
        """ Get Value From Alias

        :param alias:
        :param key:
        :return:
        """
        try:
            if key is None:
                return self.contract_data[alias]
            return self.contract_data[alias][key]
        except KeyError:
            raise KeyError
        except Exception as err:
            print(type(err), err)
