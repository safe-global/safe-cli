from prompt_toolkit.formatted_text import HTML

SAFE_ARGUMENT_COLOR = "em"
SAFE_EMPTY_ARGUMENT_COLOR = "ansimagenta"


safe_commands_arguments = {
    "add_delegate": "<address> <label> <signer-address>",
    "add_owner": "<address> [--threshold <int>]",
    "approve_hash": "<safe-tx-hash> <address>",
    "balances": "(read-only)",
    "batch-txs": "<safe-nonce> <safe-tx-hash> [ <safe-tx-hash> ... ]",
    "change_fallback_handler": "<address>",
    "change_guard": "<address>",
    "change_master_copy": "<address>",
    "change_threshold": "<address>",
    "disable_module": "<address>",
    "enable_module": "<address>",
    "execute-tx": "<safe-tx-hash>",
    "get_delegates": "(read-only)",
    "get_nonce": "(read-only)",
    "get_owners": "(read-only)",
    "get_threshold": "(read-only)",
    "history": "(read-only)",
    "info": "(read-only)",
    "load_cli_owners": "<account-private-key> [<account-private-key>...]",
    "load_ledger_cli_owners": "[--legacy-accounts] [--derivation-path <str>]",
    "load_trezor_cli_owners": "[--legacy-accounts] [--derivation-path <str>]",
    "load_cli_owners_from_words": "<word_1> <word_2> ... <word_12>",
    "refresh": "",
    "remove_delegate": "<address> <signer-address>",
    "remove_owner": "<address> [--threshold <int>]",
    "remove_proposed_transaction": "safe-tx-hash",
    "send_custom": "<address> <value-wei> <data> [--delegate] [--safe-nonce <int>]",
    "send_erc20": "<address> <token-address> <value-wei> [--safe-nonce <int>]",
    "send_erc721": "<address> <token-address> <token-id> [--safe-nonce <int>]",
    "send_ether": "<address> <value-wei> [--safe-nonce <int>]",
    "show_cli_owners": "(read-only)",
    "sign_message": "[--eip191_message <str>] [--eip712_path <file-path>]",
    "sign-tx": "<safe-tx-hash>",
    "unload_cli_owners": "<address> [<address>...]",
    "update": "",
    "update_version_to_l2": "<address>",
    "blockchain": "",
    "tx-service": "",
    "drain": "<address>",
}

safe_commands = list(safe_commands_arguments.keys())

safe_color_arguments = {
    "(read-only)": SAFE_ARGUMENT_COLOR,
    "<account-private-key>": SAFE_ARGUMENT_COLOR,
    "<address>": SAFE_ARGUMENT_COLOR,
    "<hex-str>": SAFE_ARGUMENT_COLOR,
    "<integer>": SAFE_ARGUMENT_COLOR,
    "<safe-tx-hash>": SAFE_ARGUMENT_COLOR,
    "<token-address>": SAFE_ARGUMENT_COLOR,
    "<token-id>": SAFE_ARGUMENT_COLOR,
    "<value-wei>": SAFE_ARGUMENT_COLOR,
}

meta = {
    "approve_hash": HTML(
        "<b>approve_hash</b> will approve a safe-tx-hash for the provided sender address. "
        "Sender private key must be loaded first"
    ),
    "balances": HTML(
        "<b>balances</b> will return the balance of Ether and ERC20 tokens of the Safe "
        "(if tx service available for the network)"
    ),
    "history": HTML(
        "<b>history</b> will return information of last transactions for the Safe "
        "(if tx service available for the network)"
    ),
    "batch-txs": HTML(
        "<b>batch-txs</b> will take pending or executed transactions by safe tx hash and will create a new"
        "transaction using the provided safe nonce"
    ),
    "execute-tx": HTML(
        "Take a pending transaction from Safe Tx Service and execute it using a loaded sender"
    ),
    "sign-tx": HTML(
        "<b>sign-tx</b> will sign the provided safeTxHash using the owners loaded on the CLI"
    ),
    "sign_message": HTML(
        "<b>sign_message</b> sign the provided string message provided by standard input or the EIP712 provided by file"
    ),
    "info": HTML(
        "<b>info</b> will return all the information available for a Safe, with Gnosis Tx Service and "
        "Etherscan links if the network is supported"
    ),
    "show_cli_owners": HTML(
        "Command <b>show_cli_owners</b> will return a list of loaded <u>&lt;address&gt;</u> "
        "account owners."
    ),
    "get_owners": HTML(
        "Command <b>get_owners</b> will return a list of check-summed <u>&lt;address&gt;</u> "
        "account owners."
    ),
    "get_delegates": HTML(
        "Command <b>get_delegates</b> will return information about the current delegates."
    ),
    "change_owner": HTML(
        "Command <b>change_owner</b> will change an old account <u>&lt;address&gt;</u> for the new "
        "check-summed <u>&lt;address&gt;</u> account."
    ),
    "add_owner": HTML(
        "Command <b>add_owner</b> will add a check-summed <u>&lt;address&gt;</u> owner account."
    ),
    "remove_owner": HTML(
        "Command <b>remove_owner</b> will remove an old account <u>&lt;address&gt;</u> from the "
        "current loaded safe."
    ),
    "add_delegate": HTML(
        "Command <b>add_delegate</b> will add a check-summed <u>&lt;address&gt;</u> delegate account."
    ),
    "remove_delegate": HTML(
        "Command <b>remove_delegate</b> will remove a delegate <u>&lt;address&gt;</u> from the "
        "current loaded safe."
    ),
    "remove_proposed_transaction": HTML(
        "Command <b>remove_proposed_transaction</b> will remove proposed not executed transaction for "
        "provided<u>&lt;safe-tx-hash&gt;</u>"
    ),
    "enable_module": HTML(
        "Command <b>enable_module</b> will enable a check-summed <u>&lt;address&gt;</u> module."
    ),
    "disable_module": HTML(
        "Command <b>disable_module</b> will disable a check-summed <u>&lt;address&gt;</u> module."
    ),
    "get_threshold": HTML(
        "Command <b>get_threshold</b> will return the threshold <u>&lt;value&gt;</u> for"
        " the current loaded safe."
    ),
    "get_nonce": HTML(
        "Command <b>get_nonce</b> will return the nonce <u>&lt;value&gt;</u> for "
        "the current loaded safe."
    ),
    "change_threshold": HTML(
        "Command <b>change_threshold</b> will change the current threshold <u>&lt;integer&gt;</u> "
        "value for the loaded safe."
    ),
    "send_custom": HTML(
        "Command <b>send_custom</b> will try to send a custom tx to a check-summed account. Set value "
        "to 0 if you don't want to send ether. <b>--delegate</b> can be added to send a DELEGATECALL"
    ),
    "send_ether": HTML(
        "Command <b>send_ether</b> will try to send Wei <u>&lt;value&gt;</u> to a check-summed account"
        " <u>&lt;address&gt;</u> if enough funds are found, withing the current loaded safe."
    ),
    "send_erc20": HTML(
        "Command <b>send_erc20</b> will try to send a Token <u>&lt;value&gt;</u> from a check-summed "
        "<u>&lt;token-address&gt;</u>, to a check-summed account <u>&lt;address&gt;</u> if enough funds"
        " are found, withing the current loaded safe."
    ),
    "send_erc721": HTML(
        "Command <b>send_erc721</b> will try to send a ERC 721 Token <u>&lt;value&gt;</u>"
        "from a check-summed <u>&lt;token-address&gt;</u>, to a check-summed account "
        "<u>&lt;address&gt;</u>."
    ),
    "unload_cli_owners": HTML(
        "Command <b>unload_cli_owners</b> will unload a check-summed <u>&lt;address&gt;</u> "
        "from the current loaded account owners."
    ),
    "load_cli_owners": HTML(
        "Command <b>load_cli_owners</b> will try to load a new owner via "
        "<u>&lt;account-private-key&gt;</u>."
    ),
    "load_ledger_cli_owners": HTML(
        "Command <b>load_ledger_cli_owners</b> show a list of Ledger hardware wallet addresses to choose between them "
    ),
    "load_trezor_cli_owners": HTML(
        "Command <b>load_trezor_cli_owners</b> show a list of Trezor hardware wallet addresses to choose between them "
    ),
    "load_cli_owners_from_words": HTML(
        "Command <b>load_cli_owners_from_words</b> will try to load owners via"
        "<u>seed_words</u>. Only relevant accounts(owners) will be loaded"
    ),
    "refresh": HTML(
        "Command <b>refresh</b> will refresh the information for the current loaded safe."
    ),
    "change_master_copy": HTML(
        "Command <b>change_master_copy</b> will change the current MasterCopy of the "
        "Safe Contract <b>[DO NOT CALL THIS FUNCTION, UNLESS YOU KNOW WHAT YOU ARE DOING. "
        "ALL YOUR FUNDS COULD BE LOST]</b>."
    ),
    "change_fallback_handler": HTML(
        "Command <b>change_fallback_handler</b> will change the current "
        "fallbackHandler for Safes with version >= 1.1.0 "
        "<b>[DO NOT CALL THIS FUNCTION, UNLESS YOU KNOW WHAT YOU ARE DOING. "
        "ALL YOUR FUNDS COULD BE LOST]</b>."
    ),
    "change_guard": HTML(
        "Command <b>change_guard</b> will change the current "
        "guard for Safes with version >= 1.3.0 "
        "<b>[DO NOT CALL THIS FUNCTION, UNLESS YOU KNOW WHAT YOU ARE DOING. "
        "ALL YOUR FUNDS COULD BE LOST]</b>."
    ),
    "update": HTML(
        "Command <b>update</b> will upgrade the Safe master copy to the latest version"
    ),
    "update_version_to_l2": HTML(
        "Updates a v1.1.1/v1.3.0/v1.4.1 non L2 Safe to a L2 Safe supported by Safe Wallet UI. "
        "The migration contract address needs to be provided. Nonce for the Safe must be 0."
    ),
    "blockchain": HTML(
        "<b>blockchain</b> sets the default mode for tx service. Transactions will be "
        "sent to blockchain"
    ),
    "tx-service": HTML(
        "<b>tx-service</b> enables tx-service integration. Transactions will be sent to the tx-service "
        "instead of blockchain, so they will show up on the interface"
    ),
    "drain": HTML(
        "Command <b>drain</b> will try to send all assets ether and ERC20 to a check-summed account"
    ),
}
