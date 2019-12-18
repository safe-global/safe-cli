#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class SafeUtils:
    def __init__(self, logger, safe_interface):
        self.name = self.__class__.__name__
        self.logger = logger
        self.safe_interface = safe_interface
        self.safe_operator = self.safe_interface.safe_operator

    def setinel_helper(self, address_value):
        """ Sender Helper
        This function calculate the sentinel for an owner within the safe-cli
        :param address_value:
        :return:
        """
        previous_owner = '0x' + ('0' * 39) + '1'
        owner_list = self.safe_operator.retrieve_owners()
        self.logger.debug0('[ Current Owner with Address to be Removed ]: {0}'.format(str(address_value)))
        self.logger.debug0('[ Current Local Account Owners ]: {0}'.format(owner_list))

        for index, owner_address in enumerate(owner_list):
            if address_value == owner_address:
                self.logger.info('[ Found Owner in Owners ]: {0} with Index {1}'.format(owner_address, index))
                try:
                    sentinel_index = (index - 1)
                    self.logger.debug0('[ SENTINEL Address Index ]: {0}'.format(sentinel_index))
                    if index != 0:
                        previous_owner = owner_list[(index - 1)]
                    self.logger.info('[ Found PreviousOwner on the list ]: {0}'.format(previous_owner))
                    return previous_owner
                except IndexError:
                    self.logger.error('Sentinel Address not found, returning NULLADDRESS')
