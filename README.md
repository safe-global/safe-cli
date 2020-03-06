# Safe-CLI
Command line utility for **Gnosis Safe** contracts. Use it to manage your **Gnosis Safe** easily from the command line

## Installing
**Python >= 3.7** is required. **Python 3.8** is recommended.

```bash
stat venv 2>/dev/null || python -m venv venv
source venv/bin/activate && pip install -r requirements.txt
```

## Using
```bash
source venv/bin/activate
python safe_cli.py <checksummed_safe_address> <ethereum_node_url>
```

Then you should be on the prompt and see information about the Safe, like the owners, version, etc.
Next step would be loading some owners for the Safe. At least `threshold` owners need to be loaded to do operations
on the Safe and at least one of them should have funds for sending transactions.

Loading owners is not needed if you just want to do `read-only` operations.

To load owners:
```
> load_cli_owners <account_private_key>
Loaded account 0xab...cd with balance=123 ether
Set account 0xab..cd as default sender of txs
```

To check the loaded owners:
```
> show_cli_owners
```

To unload an owner:
```
> unload_cli_owners <ethereum_checksummed_address>
```

Operations currently supported:
- `send_ether <address> <value-wei>`: Sends ether from the Gnosis Safe to another account
- `send_erc20 <address> <token_address> <value>`: Send ERC20 token from the Gnosis Safe to another account
- `add_owner <address>`: Adds a new owner `address` to the Safe.
- `remove_owner <address>`: Removes an owner `address` from the Safe.
- `change_threshold <integer>`: Changes the `threshold` of the Safe.
- `change_master_copy <address>`: Updates the master copy to be `address`. It's used to update the Safe.
**WARNING: DON'T CALL THIS IF YOU DON'T KNOW WHAT YOU ARE DOING. ALL YOUR FUNDS COULD BE LOST**

If the information in the information bar is outdated or there's any problem you can force the `safe-cli` to update
the information about the Safe using:
```
> refresh
```

Contributors
------------
- Pedro Arias Ruiz
- Uxío Fuentefría (uxio@gnosis.pm)
