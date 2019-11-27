#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Pandas Package
import pandas as pd
from pandas import DataFrame

# Configure Pandas Term Output
pd.set_option('display.max_rows', 750)
pd.set_option('display.max_columns', 750)
pd.set_option('display.width', 1400)


class TransactionHistoryManager:
    def __init__(self):
        self.name = self.__class__.__name__
        self.history = DataFrame()

        self._properties = {
            'name': self.name,
            'history': self.history,
        }

    def __getitem__(self, _key):
        if _key == 'properties':
            return self._properties
        return self._properties[_key]

    # Todo: Add Receipt Data in Update.
    # def update_tx_status_dataframe_row(self, dataframe, index, column, _tx_receipt):
    #     dataframe.loc[dataframe.index == index, 'tx_status'] = column
    #     return dataframe

    def update_history(self, updated_tx_history):
        self.history = updated_tx_history
        self._properties['history'] = self.history

    @staticmethod
    def __eval_empty_value(value, key=''):
        try:
            if value is None:
                return 'N/A'
            return value[key]
        except KeyError or TypeError:
            return 'N/A'

    def add_tx_to_history(self, _provider, _from, _tx_receipt, _tx_data):
        """ Add Transaction
        This function adds a new entry into the transaction history
        :param _provider:
        :param _from:
        :param _tx_receipt:
        :param _tx_data:
        :return:
        """
        transaction_data = {
            'provider': [_provider],
            'from': [_from],
            'nonce': [self.__eval_empty_value(_tx_data, 'nonce')],
            'gasPrice': [self.__eval_empty_value(_tx_data, 'gasPrice')],
            'gas': [self.__eval_empty_value(_tx_data, 'gas')],
            'value': [self.__eval_empty_value(_tx_data, 'value')],
            'blockHash': [self.__eval_empty_value(_tx_receipt, 'blockHash')],
            'blockNumber': [self.__eval_empty_value(_tx_receipt, 'blockNumber')],
            'contractAddress': [self.__eval_empty_value(_tx_receipt, 'contractAddress')],
            'cumulativeGasUsed': [self.__eval_empty_value(_tx_receipt, 'cumulativeGasUsed')],
            'gasUsed': [self.__eval_empty_value(_tx_receipt, 'gasUsed')],
            'logs': [self.__eval_empty_value(_tx_receipt, 'logs')],
            'root': [self.__eval_empty_value(_tx_receipt, 'root')],
            'to': [self.__eval_empty_value(_tx_receipt, 'to')],
            'transactionHash': [self.__eval_empty_value(_tx_receipt, 'transactionHash')],
            'transactionIndex': [self.__eval_empty_value(_tx_receipt, 'transactionIndex')]
        }

        # note: removed log, provider, root from view, to better manage the output space (FULL LIST HERE)
        # columns = [
        #     'provider', 'from', 'nonce', 'gasPrice', 'blockHash', 'value', 'blockNumber', 'contractAddress',
        #     'cumulativeGasUsed', 'gasUsed', 'logs', 'root', 'to', 'transactionHash', 'transactionIndex'
        # ]
        new_row = DataFrame(
            transaction_data,
            columns=[
               'from', 'nonce', 'gasPrice', 'blockHash', 'value', 'blockNumber', 'contractAddress', 'cumulativeGasUsed', 'gasUsed', 'to', 'transactionHash', 'transactionIndex'
            ]
        )
        self.update_history(self.history.append(new_row, ignore_index=True))


