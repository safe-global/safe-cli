#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class EtherHelper:
    """ Ether Helper
    This class will help the sendEther function when it's triggered, unifying ether badges previous the start of the
    ether transaction
    """
    def __init__(self, logger, ethereum_client):
        self.name = self.__class__.__name__
        self.logger = logger
        self.ethereum_client = ethereum_client

    def get_proper_ether_amount(self, wei_amount):
        """ Get Proper Ether Amount
        This function will show a human readable ammount of ether when a command view related with ether it's triggered
        :param wei_amount:
        :return:
        """
        k_ether = self.ethereum_client.w3.toWei(1, 'kether')
        m_ether = self.ethereum_client.w3.toWei(1, 'mether')
        g_ether = self.ethereum_client.w3.toWei(1, 'gether')
        t_ether = self.ethereum_client.w3.toWei(1, 'tether')

        if wei_amount >= t_ether:
            return 'T-Ether', self.ethereum_client.w3.fromWei(wei_amount, 'tether')
        elif wei_amount >= g_ether:
            return 'G-Ether', self.ethereum_client.w3.fromWei(wei_amount, 'gether')
        elif wei_amount >= m_ether:
            return 'M-Ether', self.ethereum_client.w3.fromWei(wei_amount, 'mether')
        elif wei_amount >= k_ether:
            return 'K-Ether', self.ethereum_client.w3.fromWei(wei_amount, 'kether')
        else:
            return 'Ether', self.ethereum_client.w3.fromWei(wei_amount, 'ether')

    def unify_ether_badge_amounts(self, ether_badge, ether_amounts):
        """ Unify Ether Badge Amounts
        This function will transform a list of ether values of a concrete badge into wei, so later i can be sum up
        and send
        :param ether_badge:
        :param ether_amounts:
        :return:
        """
        ether_amount = 0
        if ether_amounts:
            self.logger.debug0('[ Badge Id ]: {0:^14} | {1}'.format(ether_badge, ether_amounts))
            for ether_badge_amount in ether_amounts:
                if ether_badge == '--wei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'wei')
                elif ether_badge == '--kwei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'kwei')
                elif ether_badge == '--babbage':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'babbage')
                elif ether_badge == '--mwei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'mwei')
                elif ether_badge == '--lovelace':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'lovelace')
                elif ether_badge == '--picoether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'picoether')
                elif ether_badge == '--gwei':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'gwei')
                elif ether_badge == '--shannon':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'shannon')
                elif ether_badge == '--nanoether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'nanoether')
                elif ether_badge == '--szabo':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'szabo')
                elif ether_badge == '--microether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'microether')
                elif ether_badge == '--micro':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'micro')
                elif ether_badge == '--finney':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'finney')
                elif ether_badge == '--milliether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'milliether')
                elif ether_badge == '--milli':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'milli')
                elif ether_badge == '--ether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'ether')
                elif ether_badge == '--kether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'kether')
                elif ether_badge == '--grand':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'grand')
                elif ether_badge == '--mether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'kether')
                elif ether_badge == '--gether':
                    ether_amount += self.ethereum_client.w3.toWei(ether_badge_amount, 'gether')
            return ether_amount
        return 0

    def get_unify_ether_amount(self, ether_badge_parsed_list):
        """ Get Unify Ether Amount
        This function will trigger the sum for each type of badges
        :param ether_badge_parsed_list:
        :return:
        """
        final_amount = 0
        for item_data in ether_badge_parsed_list:
            final_amount += self.unify_ether_badge_amounts(item_data[0], item_data[1])
        self.logger.debug0('{0} Ether'.format(self.ethereum_client.w3.fromWei(final_amount, 'ether')))
        return final_amount

    def get_simplified_balance(self, sender_address):
        balance = self.ethereum_client.w3.eth.getBalance(sender_address)
        wei_amount = self.get_unify_ether_amount([('--wei', [balance])])
        return self.get_proper_ether_amount(wei_amount)
