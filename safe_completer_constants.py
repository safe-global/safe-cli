# -*- coding: utf-8 -*-

# Import HTML Module
from prompt_toolkit.formatted_text import HTML

SAFE_ARGUMENT_COLOR = 'em'
SAFE_EMPTY_ARGUMENT_COLOR = 'ansimagenta'


safe_commands = ['refresh', 'get_nonce', 'get_owners', 'get_threshold', 'show_cli_owners',
                 'load_cli_owner', 'unload_cli_owner', 'add_owner', 'change_threshold', 'remove_owner',
                 'change_master_copy', 'send_ether', 'send_erc20']

safe_commands_arguments = {
    'refresh': '',
    'show_cli_owners': '(read-only)',
    'get_threshold': '(read-only)',
    'get_owners': '(read-only)',
    'get_nonce': '(read-only)',
    'load_cli_owner': '<account-private-key>',
    'unload_cli_owner': '<address>',
    'add_owner': '<address>',
    'change_threshold': '<address>',
    'remove_owner': '<address>',
    'change_master_copy': '<address>',
    'send_ether': '<address> <token_address> <value>',
    'send_erc20': '<address> <value-wei>',
}

safe_color_arguments = {
    '(read-only)': SAFE_ARGUMENT_COLOR,
    '<address>': SAFE_ARGUMENT_COLOR,
    '<integer>': SAFE_ARGUMENT_COLOR,
    '<address> <value-wei>': SAFE_ARGUMENT_COLOR,
    '<account-private-key>': SAFE_ARGUMENT_COLOR,
    '<address> <token_address> <value>': SAFE_ARGUMENT_COLOR,
}

meta = {
    'show_cli_owners': HTML('Command <b>show_cli_owners</b> will return a list of loaded <u>&lt;address&gt;</u> '
                            'account owners.'),
    'get_owners': HTML('Command <b>get_owners</b> will return a list of check-summed <u>&lt;address&gt;</u> '
                            'account owners.'),
    'change_owner': HTML('Command <b>change_owner</b> will change an old account <u>&lt;address&gt;</u> for the new '
                         'check-summed <u>&lt;address&gt;</u> account.'),
    'add_owner': HTML('Command <b>add_owner</b> will add a check-summed <u>&lt;address&gt;</u> owner account.'),
    'remove_owner': HTML('Command <b>remove_owner</b> will remove an old account <u>&lt;address&gt;</u> from the '
                         'current loaded safe.'),
    'get_threshold': HTML('Command <b>get_threshold</b> will return the threshold <u>&lt;value&gt;</u> for'
                          ' the current loaded safe.'),
    'get_nonce': HTML('Command <b>get_nonce</b> will return the nonce <u>&lt;value&gt;</u> for '
                      'the current loaded safe.'),
    'change_threshold': HTML('Command <b>change_threshold</b> will change the current threshold <u>&lt;integer&gt;</u> '
                             'value for the loaded safe.'),
    'send_ether': HTML('Command <b>send_ether</b> will try to send a Wei <u>&lt;value&gt;</u> to a check-summed account'
                       ' <u>&lt;address&gt;</u> if enough funds are found, withing the current loaded safe.'),
    'send_erc20': HTML('Command <b>send_erc20</b> will try to send a Token <u>&lt;value&gt;</u> from a check-summed '
                       '<u>&lt;token-address&gt;</u>, to a check-summed account <u>&lt;address&gt;</u> if enough funds'
                       ' are found, withing the current loaded safe.'),
    'unload_cli_owner': HTML('Command <b>unload_cli_owner</b> will unload a check-summed <u>&lt;address&gt;</u> '
                             'from the current loaded account owners.'),
    'load_cli_owner': HTML('Command <b>load_cli_owner</b> will try to load a new owner via '
                           '<u>&lt;account-private-key&gt;</u>.'),
    'refresh': HTML('Command <b>refresh</b> will refresh the information for the current loaded safe.'),
    'change_master_copy': HTML('Command <b>change_master_copy</b> will try to update the current version of the loaded '
                               'safe <b>[DO NOT CALL THIS FUNCTION, UNLESS YOU KNOW WHAT YOU ARE DOING. '
                               'ALL YOUR FUNDS COULD BE LOST]</b>.'),
}
