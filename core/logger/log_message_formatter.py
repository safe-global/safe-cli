#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Aesthetics Constants
from core.constants.console_constant import STRING_DASHES

# Import HexBytes for visual information in the logger
from hexbytes import HexBytes


class LogMessageFormatter:
    """ Logging Message Formatter
    """
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger
        self.empty_value = ' - Empty - '

    def log_dash_splitter(self):
        self.logger.info(' ' + STRING_DASHES)

    def log_error_footer(self, msg='Error.'):
        message = self.header_block(msg, '-')
        self.logger.error(message)

    def log_header(self, msg='Success.'):
        message = self.header_block(msg, '-')
        self.logger.info(message)

    def log_banner_header(self, msg='Log Head Banner'):
        message = self.header_block(msg, '=')
        self.logger.info(' ' + message)

    def log_entry_message(self, msg='Log Entry Message'):
        self.logger.info(' ' + STRING_DASHES)
        self.logger.info('|{0}|'.format(self.header_block(msg=msg, filler=' ')))
        self.logger.info(' ' + STRING_DASHES)

    def log_section_left_side(self, msg='Left Side Log Header'):
        header_data = '-:[ {0} ]:-'.format(msg)
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

    def log_data(self, name=' (#) Test Name: {0} ', msg='Data'):
        information_data = name.format(msg)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

    @staticmethod
    def header_block(msg, filler=' ', str_count=140):
        """ Format Header
        This function will perform formatting a header like message being prompted in the console
        :return:
        """
        text = ':[ {0} ]:'.format(msg.title())
        return text.center(str_count, filler)

    def tx_data_formatter(self, sender_data, payload_data):
        self.log_section_left_side('Data')
        information_data = ' (#) Sender Data: {0}'.format(sender_data)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        information_data = ' (#) Payload Data: {0}'.format(payload_data)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info(' ' + STRING_DASHES)

    def tx_receipt_formatter(self, data, detailed_receipt=True):
        transaction_hash = self.empty_value
        transaction_index = self.empty_value
        block_hash = self.empty_value
        block_number = self.empty_value
        to_address = self.empty_value
        gas_used = -1
        cumulative_gas_used = -1
        contract_address = self.empty_value
        status = self.empty_value
        signature_v = HexBytes(b'').hex()
        signature_r = HexBytes(b'').hex()
        signature_s = HexBytes(b'').hex()

        try:
            transaction_hash = HexBytes(data.transactionHash).hex()
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve transaction_hash, setting value to default')

        try:
            transaction_index = data.transactionIndex
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve transaction_index, setting value to default')

        try:
            block_hash = HexBytes(data.blockHash).hex()
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve block_hash, setting value to default')

        try:
            block_number = data.blockNumber
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve block_number, setting value to default')

        try:
            to_address = data.to
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve block_number, setting value to default')

        try:
            gas_used = data.gasUsed
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve gas_used, setting value to default')

        try:
            cumulative_gas_used = data.cumulativeGasUsed
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve cumulative_gas_used, setting value to default')

        try:
            contract_address = data.contractAddress
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve contract_address, setting value to default')

        try:
            status = data.status
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve status, setting value to default')

        try:
            logs_bloom = HexBytes(data.logsBloom).hex()
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve logs_bloom, setting value to default')

        try:
            signature_v = HexBytes(data.v).hex()
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve signature_v, setting value to default')

        try:
            signature_r = HexBytes(data.r).hex()
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve signature_r, setting value to default')

        try:
            signature_s = HexBytes(data.s).hex()
        except Exception as err:
            self.logger.debug0(err)
            self.logger.debug0('Unable to Retrieve signature_s, setting value to default')

        header_data = '-:[ {0} ]:-'.format('Safe Tx Receipt')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

        information_data = ' (#) Address To: {0} Contract Address: {1}'.format(to_address, contract_address)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        information_data = ' (#) Status: {0} | Tx Index: {1} | Tx Hash: {2}'.format(status, transaction_index,
                                                                                    transaction_hash)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        information_data = ' (#) Block Number: {0} | Block Hash: {1}'.format(block_number, block_hash)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        information_data = ' (#) Gas Used: {0} | Cumulative Gas Used: {1}'.format(gas_used, cumulative_gas_used)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        if str(signature_v) != '0x':
            information_data = ' (#) Signature v: {0}'.format(signature_v)
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        if str(signature_r) != '0x':
            information_data = ' (#) Signature r: {0}'.format(signature_r)
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        if str(signature_s) != '0x':
            information_data = ' (#) Signature s: {0}'.format(signature_s)
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        # information_data = ' (#) LogsBloom: {0}'.format(logs_bloom)
        # self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        if detailed_receipt:
            for item_index, item_logs in enumerate(data.logs):
                log_transaction_hash = HexBytes(b'').hex()
                log_block_hash = HexBytes(b'').hex()
                log_block_number = -1
                log_address = self.empty_value
                log_data = self.empty_value
                log_topic = HexBytes(b'').hex()
                log_mined = self.empty_value

                try:
                    log_transaction_hash = HexBytes(item_logs['transactionHash']).hex()
                except Exception as err:
                    self.logger.debug0(err)
                    self.logger.debug0('Unable to Retrieve log_transaction_hash, setting value to default')

                try:
                    log_block_hash = HexBytes(item_logs['blockHash']).hex()
                except Exception as err:
                    self.logger.debug0(err)
                    self.logger.debug0('Unable to Retrieve log_block_hash, setting value to default')

                try:
                    log_block_number = item_logs['blockNumber']
                except Exception as err:
                    self.logger.debug0(err)
                    self.logger.debug0('Unable to Retrieve log_block_number, setting value to default')

                try:
                    log_address = item_logs['address']
                except Exception as err:
                    self.logger.debug0(err)
                    self.logger.debug0('Unable to Retrieve log_address, setting value to default')

                try:
                    log_data = item_logs['data']
                except Exception as err:
                    self.logger.debug0(err)
                    self.logger.debug0('Unable to Retrieve log_data, setting value to default')

                try:
                    log_topic = HexBytes(item_logs['topics'][0]).hex()
                except Exception as err:
                    self.logger.debug0(err)
                    self.logger.debug0('Unable to Retrieve log_topic, setting value to default')

                try:
                    log_mined = item_logs['type']
                except Exception as err:
                    self.logger.debug0(err)
                    self.logger.debug0('Unable to Retrieve log_mined, setting value to default')

                header_data = '-:[ {0} {1} ]:-'.format('Tx Log Number', item_index)
                self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

                information_data = ' (#) Address To: {0}'.format(log_address)
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

                information_data = ' (#) Tx Hash: {0}'.format(log_transaction_hash)
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

                information_data = ' (#) Block Number: {0} | Block Hash: {1}'.format(log_block_number, log_block_hash)
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

                information_data = ' (#) Data:'
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
                self.logger.info('|    {0}{1}|'.format(log_data, ' ' * (140 - len(log_data) - 4)))

                information_data = ' (#) Topic: {0} | Type: {1}'.format(log_topic, log_mined)
                self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

        self.logger.info(' ' + STRING_DASHES)
