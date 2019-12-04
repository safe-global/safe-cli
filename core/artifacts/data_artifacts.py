#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DataArtifacts:
    def __init__(self, logger, account_artifacts, payload_artifacts, token_artifacts, contract_artifacts):
        self.name = self.__class__.__name__
        self.logger = logger
        # Data Artifacts
        self.account_artifacts = account_artifacts
        self.payload_artifacts = payload_artifacts
        self.token_artifacts = token_artifacts
        self.contract_artifacts = contract_artifacts

    def artifact_selection(self, artifact_type):
        if artifact_type == 'account':
            return self.account_artifacts.account_data
        elif artifact_type == 'payload':
            return self.payload_artifacts.payload_data
        elif artifact_type == 'token':
            return self.token_artifacts.token_data
        elif artifact_type == 'contract':
            return self.contract_artifacts.contract_data

    def retrive_from_stored_values(self, alias, key=None, artifact_type=None):
        try:
            self.logger.debug0('Searching for Stored Artifact: [ Alias ( {0} ) | Key ( {1} ) | Artifact Type ( {2} ) ]'.format(alias, key, artifact_type))
            artifact_data = self.artifact_selection(artifact_type)
            try:
                if key is None:
                    data = artifact_data[alias]
                    self.logger.debug0('Data Found without Key: [ Alias ( {0} ) | Data ( {1} ) ]'.format(alias, data))
                    return data
                data = artifact_data[alias][key]
                self.logger.debug0('Data Found with Key: [ Alias ( {0} ) | Key ( {1} ) | Data ( {2} ) ]'.format(alias, key, data))
                return data
            except KeyError:
                self.logger.error('Unable to find the proper value for key & alias provided')
        except Exception as err:
            self.logger.error('Unknown Error: [ Type ( {0} ) | Error ( {1} ) ]'.format(type(err), err))

    def from_alias_get_value(self, stream_value, artifact_type=None):
        """ From Alias get Value
        This function will retrieve the data from a given value
        :param stream:
        :return:
        """
        value_from_artifact = ''
        artifact_data = self.artifact_selection(artifact_type)
        for item in artifact_data:
            if stream_value.startswith(item):
                try:
                    alias = stream_value.split('.')[0]
                    key = stream_value.split('.')[1]
                    value_from_artifact = self.retrive_from_stored_values(alias, key, artifact_type)
                except IndexError:
                    self.logger.error('Unable to parse substring value from_alias_get_value()')
        self.logger.debug0('From Alias Get Value | StreamValue: {0} | Value: {1} | '.format(stream_value, value_from_artifact))
        return value_from_artifact