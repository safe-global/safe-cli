
class SafeEther:
    def __init__(self, logger, safe_interface, safe_transaction):
        self.name = self.__class__.__name__
        self.logger = logger

        self.safe_interface = safe_interface
        self.safe_transaction = safe_transaction

    def command_send_ether(self, address_to, wei_amount, local_account, _execute=False, _queue=False):
        """ Command Send Ether
        This function will send ether to the address_to, wei_amount, from private_key
        :param address_to:
        :param wei_amount:
        :param local_account:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current ether balance of the safe before the transaction
            self.command_view_ether_balance()

            # Compose the transaction for sendEther
            signed_tx = self.ethereum_client.w3.eth.account.signTransaction(dict(
                nonce=self.ethereum_client.w3.eth.getTransactionCount(local_account.address),
                gasPrice=self._fix_gas_price(),
                gas=self.base_gas,
                to=address_to,
                value=self.ethereum_client.w3.toWei(wei_amount, 'wei')
            ), HexBytes(local_account.privateKey).hex())

            if _execute:
                # Sign the transaction
                tx_hash = self.ethereum_client.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

                # Perform the transaction
                tx_receipt = self.ethereum_client.get_transaction_receipt(tx_hash, timeout=60)

                # Format Receipt with Logger
                self.log_formatter.tx_receipt_formatter(tx_receipt, detailed_receipt=True)

            elif _queue:
                self.tx_queue.append('Not sendEther/depositEther')

            # Preview the current ether balance of the safe after the transaction
            self.command_view_ether_balance()
        except Exception as err:
            self.logger.error('Unable to command_send_ether_raw(): {0} {1}'.format(type(err), err))


    def command_deposit_ether(self, wei_amount, local_account, _execute=False, _queue=False):
        """ Command Deposit Ether
        This function will send ether to the address_to, wei_amount
        :param wei_amount:
        :param local_account:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Compose transaction for depositEther
            self.command_send_ether(self.safe_operator.address, wei_amount, local_account, _execute=_execute, _queue=_queue)
        except Exception as err:
            self.logger.error('Unable to command_deposit_ether_raw(): {0} {1}'.format(type(err), err))


    def command_withdraw_ether(self, wei_amount, address_to, _execute=False, _queue=False):
        """ Command Withdraw Ether
        This function will send ether to the address_to, wei_amount
        :param wei_amount:
        :param address_to:
        :param _execute:
        :param _queue:
        :return:
        """
        try:
            # Preview the current ether balance of the safe before the transaction
            self.command_view_ether_balance()

            # Perform the transaction
            self.perform_transaction(b'', wei_amount, address_to, _execute=_execute, _queue=_queue)

            # Preview the current ether balance of the safe after the transaction
            self.command_view_ether_balance()
        except Exception as err:
            self.logger.error('Unable to command_withdraw_ether_raw(): {0} {1}'.format(type(err), err))


    def command_view_balance(self):
        """ Command View Total Balance of the safe Ether + Tokens(Only if tokens are known via pre-loading)
        This function
        """
        self.command_view_ether_balance()
        self.command_view_token_balance()


    def command_view_ether_balance(self):
        """ Command View Ether Balance
        This function will show the balance of the safe & the owners
        """
        try:
            self.log_formatter.log_section_left_side('Safe Ether Balance')
            ether_amount = []
            for owner_index, owner in enumerate(self.safe_instance.functions.getOwners().call()):
                ether_amount.append(self.ethereum_client.w3.eth.getBalance(owner))

            # Calculate ether amount for the Owners
            wei_amount = self.ether_helper.unify_ether_badge_amounts('--wei', ether_amount)
            human_readable_ether = self.ether_helper.get_proper_ether_amount(wei_amount)
            information_data = ' (#) Total Owners Funds: {0} {1} '.format(
                human_readable_ether[1], human_readable_ether[0])
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))

            # Calculate ether amount for the Safe
            safe_ether_amount = self.ethereum_client.w3.eth.getBalance(self.safe_instance.address)
            safe_wei_amount = self.ether_helper.unify_ether_badge_amounts('--wei', [safe_ether_amount])
            safe_human_readable_ether = self.ether_helper.get_proper_ether_amount(safe_wei_amount)
            information_data = ' (#) Total Safe Funds: {0} {1} '.format(
                safe_human_readable_ether[1], safe_human_readable_ether[0])
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
            self.logger.info(' ' + STRING_DASHES)
        except Exception as err:
            self.logger.error('Unable to command_view_ether_balance(): {0} {1}'.format(type(err), err))