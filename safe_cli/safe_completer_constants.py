from prompt_toolkit.formatted_text import HTML

SAFE_ARGUMENT_COLOR = 'em'
SAFE_EMPTY_ARGUMENT_COLOR = 'ansimagenta'


safe_commands_arguments = {
    'add_owner': '<address>',
    'balances': '(read-only)',
    'change_fallback_handler': '<address>',
    'change_master_copy': '<address>',
    'change_threshold': '<address>',
    'disable_module': '<address>',
    'enable_module': '<address>',
    'get_nonce': '(read-only)',
    'get_owners': '(read-only)',
    'get_threshold': '(read-only)',
    'history': '(read-only)',
    'info': '(read-only)',
    'load_cli_owners': '<account-private-key>',
    'update': '',
    'refresh': '',
    'remove_owner': '<address>',
    'send_erc20': '<address> <token_address> <value> [--safe-nonce <int>] [--tx-service]',
    'send_erc721': '<address> <token_address> <token_id> [--safe-nonce <int>] [--tx-service]',
    'send_custom': '<address> <value-wei> <data> [--delegate] [--safe-nonce <int>] [--tx-service]',
    'send_ether': '<address> <value-wei> [--safe-nonce <int>] [--tx-service]',
    'show_cli_owners': '(read-only)',
    'unload_cli_owners': '<address>',
}

safe_commands = list(safe_commands_arguments.keys())

safe_color_arguments = {
    '(read-only)': SAFE_ARGUMENT_COLOR,
    '<address>': SAFE_ARGUMENT_COLOR,
    '<integer>': SAFE_ARGUMENT_COLOR,
    '<hex-str>': SAFE_ARGUMENT_COLOR,
    '<address> <value-wei>': SAFE_ARGUMENT_COLOR,
    '<account-private-key>': SAFE_ARGUMENT_COLOR,
    '<address> <token_address> <value>': SAFE_ARGUMENT_COLOR,
}

meta = {
    'balances': HTML('<b>balances</b> will return the balance of Ether and ERC20 tokens of the Safe '
                     '(if tx service available for the network)'),
    'history': HTML('<b>history</b> will return information of last transactions for the Safe '
                    '(if tx service available for the network)'),
    'info': HTML('<b>info</b> will return all the information available for a Safe, with Gnosis Tx Service and '
                 'Etherscan links if the network is supported'),
    'show_cli_owners': HTML('Command <b>show_cli_owners</b> will return a list of loaded <u>&lt;address&gt;</u> '
                            'account owners.'),
    'get_owners': HTML('Command <b>get_owners</b> will return a list of check-summed <u>&lt;address&gt;</u> '
                       'account owners.'),
    'change_owner': HTML('Command <b>change_owner</b> will change an old account <u>&lt;address&gt;</u> for the new '
                         'check-summed <u>&lt;address&gt;</u> account.'),
    'add_owner': HTML('Command <b>add_owner</b> will add a check-summed <u>&lt;address&gt;</u> owner account.'),
    'remove_owner': HTML('Command <b>remove_owner</b> will remove an old account <u>&lt;address&gt;</u> from the '
                         'current loaded safe.'),
    'enable_module': HTML('Command <b>enable_module</b> will enable a check-summed <u>&lt;address&gt;</u> module.'),
    'disable_module': HTML('Command <b>disable_module</b> will disable a check-summed <u>&lt;address&gt;</u> module.'),
    'get_threshold': HTML('Command <b>get_threshold</b> will return the threshold <u>&lt;value&gt;</u> for'
                          ' the current loaded safe.'),
    'get_nonce': HTML('Command <b>get_nonce</b> will return the nonce <u>&lt;value&gt;</u> for '
                      'the current loaded safe.'),
    'change_threshold': HTML('Command <b>change_threshold</b> will change the current threshold <u>&lt;integer&gt;</u> '
                             'value for the loaded safe.'),
    'send_custom': HTML("Command <b>send_custom</b> will try to send a custom tx to a check-summed account. Set value "
                        "to 0 if you don't want to send ether. <b>--delegate</b> can be added to send a DELEGATECALL"),
    'send_ether': HTML('Command <b>send_ether</b> will try to send Wei <u>&lt;value&gt;</u> to a check-summed account'
                       ' <u>&lt;address&gt;</u> if enough funds are found, withing the current loaded safe.'),
    'send_erc20': HTML('Command <b>send_erc20</b> will try to send a Token <u>&lt;value&gt;</u> from a check-summed '
                       '<u>&lt;token-address&gt;</u>, to a check-summed account <u>&lt;address&gt;</u> if enough funds'
                       ' are found, withing the current loaded safe.'),
    'send_erc721': HTML('Command <b>send_erc721</b> will try to send a ERC 721 Token <u>&lt;value&gt;</u>'
                        'from a check-summed <u>&lt;token-address&gt;</u>, to a check-summed account '
                        '<u>&lt;address&gt;</u>.'),
    'unload_cli_owners': HTML('Command <b>unload_cli_owners</b> will unload a check-summed <u>&lt;address&gt;</u> '
                              'from the current loaded account owners.'),
    'load_cli_owners': HTML('Command <b>load_cli_owners</b> will try to load a new owner via '
                            '<u>&lt;account-private-key&gt;</u>.'),
    'refresh': HTML('Command <b>refresh</b> will refresh the information for the current loaded safe.'),
    'change_master_copy': HTML('Command <b>change_master_copy</b> will change the current MasterCopy of the '
                               'Safe Contract <b>[DO NOT CALL THIS FUNCTION, UNLESS YOU KNOW WHAT YOU ARE DOING. '
                               'ALL YOUR FUNDS COULD BE LOST]</b>.'),
    'change_fallback_handler': HTML('Command <b>change_fallback_handler</b> will change the current '
                                    'fallbackHandler for Safes with version >= 1.1.0 '
                                    '<b>[DO NOT CALL THIS FUNCTION, UNLESS YOU KNOW WHAT YOU ARE DOING. '
                                    'ALL YOUR FUNDS COULD BE LOST]</b>.'),
    'update': HTML('Command <b>update</b> will upgrade the Safe master copy to the latest version'),
}
