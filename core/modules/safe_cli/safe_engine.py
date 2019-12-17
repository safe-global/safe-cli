

from core.modules.safe_cli.safe_sender import SafeSender
from core.modules.safe_cli.safe_interface import SafeInterface
from core.modules.safe_cli.safe_information import SafeInformation
from core.modules.safe_cli.safe_management import SafeManagement
from core.modules.safe_cli.safe_ether import SafeEther
from core.modules.safe_cli.safe_token import SafeToken

class SafeEngine:
    def __init__(self, safe_address):
        self.name = self.__class__.__name__
        # Configure Logger Here

        self.safe_information = SafeInformation(logger, network_agent, safe_interface)
        self.safe_interface = SafeInterface(logger, network_agent, safe_address)

    def get_console_session(self):
        """ Get Console Session
        Get Console Session based on the self.active_session =
        :return:
        """
        if self.active_session is not TypeOfConsole.GNOSIS_CONSOLE:
            return PromptSession(
                completer=self.session_config['contract_completer'],
                lexer=self.session_config['contract_lexer'])

    def _setup_console_init(self, configuration):
        """ Setup Console Safe Configuration

        :param configuration:
        :return:
        """
        if configuration['safe'] is not None:
            if self.network_agent.ethereum_client.w3.isAddress(configuration['safe']):
                try:
                    self.log_formatter.log_entry_message('Entering Safe Console')
                    set_title('Safe Console')
                    self.logger.debug0(configuration['safe'])
                    self.run_safe_console(configuration['safe'], configuration['private_key'])
                except Exception as err:
                    self.logger.error('{0}'.format(self.name))
                    self.logger.error(err)
        else:
            # Info Header: Finished loading all the components of the gnosis-cli
            if not self.quiet_flag:
                self.log_formatter.log_entry_message('Entering Gnosis Cli')
            self.run_console_session(self.prompt_text)

    def run_safe_console(self, safe_address, private_key_list=None):
        """ Run Safe Console
        This function will run the safe console
        :param safe_address:
        :param private_key_list:
        :return:
        """
        try:
            self.safe_interface = ConsoleSafeCommands(safe_address, self.logger, self.data_artifacts, self.network_agent)
            if private_key_list is not None:
                self.logger.debug0(private_key_list)
                for private_key_owner in private_key_list:
                    self.safe_interface.command_load_owner(private_key_owner)
            self.active_session = TypeOfConsole.SAFE_CONSOLE
            self.run_console_session(
                prompt_text=self._get_prompt_text(affix_stream='safe-cli', stream='Safe (' + safe_address + ')'))
        except KeyError as err:
            self.logger.error(err)

    def get_toolbar_text(self, sender_address=None, sender_private_key=None):
        """ Get Toolbar Text

        :param sender_address:
        :param sender_private_key:
        :return:
        """
        amount = 0
        if (sender_address is not None) and (sender_private_key is not None):
            balance = self.network_agent.ethereum_client.w3.eth.getBalance(sender_address)
            wei_amount = self.ether_helper.get_unify_ether_amount([('--wei', [balance])])
            text_badge, tmp_amount = self.ether_helper.get_proper_ether_amount(wei_amount)
            amount = '{0} {1}'.format(str(tmp_amount), text_badge)
        return HTML(' [ <strong>Sender:</strong> %s'
                    ' | <strong>PK:</strong> %s'
                    ' | <strong>Balance:</strong> %s ]' % (sender_address, sender_private_key, amount))

    def _get_prompt_text(self, affix_stream='', stream=''):
        """ Get Prompt Text
        This function will generate the string that will be shown as the prompt text
        :param affix_stream:
        :param stream:
        :return:
        """
        return HTML('<ansiblue>[ </ansiblue><strong>./%s</strong><ansiblue> ]'
                    '[ </ansiblue><strong>%s</strong><ansiblue> ]: </ansiblue>' % (affix_stream, stream))
