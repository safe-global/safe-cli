#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Import Enum TypeOfAsset


class EthereumAssets:
    """ EthereumAssets
    This class will stored common ethereum_assets such as accounts, payloads, tokens
    & contract_artifacts
    :param logger: Logger object, init within the gnosis_manager
    :param accounts: Account assets
    :param payloads: Payload assets
    :param tokens: Token assets
    :param contracts: Contract assets
    """
    def __init__(self, logger, accounts, payloads, tokens, contracts):
        self.name = self.__class__.__name__
        self.logger = logger

        # EthereumAssets:
        self.accounts = accounts
        self.payloads = payloads
        self.tokens = tokens
        self.contracts = contracts

    def get_data_asset(self, asset_type):
        """ Artifact Selection
        This function compares the provided asset_type to the available ones stored withing the EthereumAssets
        :param asset_type:
        :return: Dict Data
        """
        if asset_type == 'account':
            return self.accounts.account_data
        elif asset_type == 'payload':
            return self.payloads.payload_data
        elif asset_type == 'token':
            return self.tokens.token_data
        elif asset_type == 'contract_cli.log':
            return self.contracts.contract_data

    def retrive_from_stored_values(self, alias, key=None, asset_type=None):
        """ Retrieve From Stored Values
        This function will retrieve stored data related to account_artifacts, payload_data, token_data, contract_data
        :param alias:
        :param key:
        :param asset_type:
        :return:
        """
        try:
            self.logger.debug0('Searching for Stored Artifact: [ Alias ( {0} ) | Key ( {1} ) | Artifact Type ( {2} ) ]'.format(alias, key, asset_type))
            asset_data = self.get_data_asset(asset_type)
            try:
                if key is None:
                    data = asset_data[alias]
                    self.logger.debug0('Data Found without Key: [ Alias ( {0} ) | Data ( {1} ) ]'.format(alias, data))
                    return data
                data = asset_data[alias][key]
                self.logger.debug0('Data Found with Key: [ Alias ( {0} ) | Key ( {1} ) | Data ( {2} ) ]'.format(
                    alias, key, data)
                )
                return data
            except KeyError:
                self.logger.error('Unable to find the proper value for key & alias provided')
        except Exception as err:
            self.logger.error('Unknown Error: [ Type ( {0} ) | Error ( {1} ) ]'.format(type(err), err))

    def from_alias_get_value(self, stream_value, asset_type=None):
        """ From Alias get Value
        This function will retrieve the data from a given value if it's stored in the data structures of the common eth_assets
        for the console (account, contract_cli.log, paload, token)
        :param stream_value:
        :param asset_type:
        :return:
        """
        value_from_artifact = ''
        asset_data = self.get_data_asset(asset_type)
        for item in asset_data:
            if stream_value.startswith(item):
                try:
                    alias = stream_value.split('.')[0]
                    key = stream_value.split('.')[1]
                    value_from_artifact = self.retrive_from_stored_values(alias, key, asset_type)
                except IndexError:
                    self.logger.error('Unable to parse substring value from_alias_get_value()')
                    return stream_value
        self.logger.debug0('From Alias Get Value | StreamValue: {0} | Value: {1} | '.format(
            stream_value, value_from_artifact)
        )
        return value_from_artifact
