[![PyPI version](https://badge.fury.io/py/safe-cli.svg)](https://badge.fury.io/py/safe-cli)
[![Build Status](https://github.com/safe-global/safe-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/safe-global/safe-cli/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/safe-global/safe-cli/badge.svg?branch=master)](https://coveralls.io/github/safe-global/safe-cli?branch=master)
![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)
![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/safeglobal/safe-cli?label=Docker&sort=semver)](https://hub.docker.com/r/safeglobal/safe-cli)

# Safe-CLI

Command line utility for **Safe** contracts. Use it to manage your **Safe** easily from the command line.

Safe-CLI does not rely on _Safe{Core} API_, so it can be used in networks where Safe services are not available. If they are available,
Safe-CLI can also interact with them in `tx-service` mode.

## Using with docker

If you have **Docker** installed on your system, you can just run:

```bash
docker run -it safeglobal/safe-cli safe-creator
```

for creating Safes

or

```bash
docker run -it safeglobal/safe-cli safe-cli
```

to run the actual **safe-cli**

## Installing

**Python >= 3.7** is required. **Python 3.10** is recommended.

```bash
pip3 install -U safe-cli
```

## Usage

```bash
safe-cli [-h] [--history] [--get-safes-from-owner] address node_url

positional arguments:
  address                The address of the Safe, or an owner address if --get-safes-from-owner is specified.
  node_url               Ethereum node url

options:
  -h, --help             Show this help message and exit
  --history              Enable history. By default it's disabled due to security reasons
  --get-safes-from-owner Indicates that address is an owner (Safe Transaction Service is required for this feature)
```

## Start Safe-CLI

To load a Safe, use the following command:

```bash
safe-cli <checksummed_safe_address> <ethereum_node_url>
```

Then you should be on the prompt and see information about the Safe, like the owners, version, etc.
Next step would be loading some owners for the Safe. At least `threshold` owners need to be loaded to do operations
on the Safe and at least one of them should have funds for sending transactions.

## Load owners

### From private key

Loading owners is not needed if you just want to do `read-only` operations.

To load owners:

```
> load_cli_owners <account_private_key>
Loaded account 0xab...cd with balance=123 ether
Set account 0xab..cd as default sender of txs
```

You can also load owners from `environment variables`. Before running the `safe-cli`:

```bash
export MY_PRIVATE_KEY=YOUR_EOA_PRIVATE_KEY
```

Run the Safe-CLI, then:

```
> load_cli_owners MY_PRIVATE_KEY
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

### From hardware wallets

**NOTE**: before signing anything ensure that the data showing on your hardware wallet device is the same as the safe-cli data.

If you want to use both `ledger` and `trezor` you need to run

```bash
pip install "safe-cli[ledger, trezor]"
```

#### Ledger

Ledger module is an optional feature of safe-cli to sign transactions with the help of [ledgereth](https://github.com/mikeshultz/ledger-eth-lib) library based on [ledgerblue](https://github.com/LedgerHQ/blue-loader-python).

To enable, safe-cli must be installed as follows:

```
pip install "safe-cli[ledger]"
```

When running on Linux, make sure the following rules have been added to `/etc/udev/rules.d/`:

```commandline
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2c97", ATTRS{idProduct}=="0000", MODE="0660", TAG+="uaccess", TAG+="udev-acl" OWNER="<UNIX username>"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2c97", ATTRS{idProduct}=="0001", MODE="0660", TAG+="uaccess", TAG+="udev-acl" OWNER="<UNIX username>"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2c97", ATTRS{idProduct}=="0004", MODE="0660", TAG+="uaccess", TAG+="udev-acl" OWNER="<UNIX username>"
```

Ledger commands:

- `load_ledger_cli_owners [--legacy-accounts] [--derivation-path <str>]`: show a list of the first 5 accounts (--legacy-accounts search using legacy derivation) or load an account from provided derivation path.

#### Trezor

Trezor module is an optional feature of safe-cli to sign transactions from Trezor hardware wallet using the [trezor](https://pypi.org/project/trezor/) library.

To enable, safe-cli must be installed as follows:

```
pip install "safe-cli[trezor]"
```

Trezor commands:

- `load_trezor_cli_owners [--legacy-accounts] [--derivation-path <str>]`: show a list of the first 5 accounts (--legacy-accounts search using legacy derivation) or load an account from provided derivation path.

## Creating a new Safe

Use `safe-creator <node_url> <private_key> --owners <checksummed_address_1> <checksummed_address_2> --threshold <uint> --salt-nonce <uint256>`.

Example:

```
safe-creator https://sepolia.infura.io/v3/$INFURA_TOKEN $PRIVATE_KEY --owners $OWNER_ADDRESS_1 [$OWNER_ADDRESS_2] --threshold 1
```

## Operating

### Modes

There are 2 operation modes:

- **blockchain**: The default mode. Use `blockchain` command to enable it. Transactions are sent to blockchain.
- **tx-service**: Use `tx-service` command to enable it. Transactions are sent to the Safe Transaction Service (if available on the network), so you will be able to see them on the Safe web interface/mobile apps. At least one signer is needed to send transactions to the service. Txs are **not executed**. It requires **_Safe{Core} API_ running on the network**.

### Common operations

**Note: Sender private key must be loaded first. When loading an owner it will be set automatically**

- `send_custom <address> <value-wei> <data-hex-str> [--delegate] [--safe-nonce <int>]`:
  Sends a custom transaction from the Safe to a contract. If `--delegate` is set a `delegatecall`
  will be triggered.
- `send_ether <address> <value-wei> [--safe-nonce <int>]`:
  Sends ether from the Safe to another account
- `send_erc20 <address> <token_address> <value> [--safe-nonce <int>]`:
  Send ERC20 token from the Safe to another account
- `approve_hash <keccak-hexstr-hash> <sender-address>`: Approves a `safe-tx-hash` for the provided sender address.
- `add_owner <address>`: Adds a new owner `address` to the Safe.
- `remove_owner <address>`: Removes an owner `address` from the Safe.
- `change_threshold <integer>`: Changes the `threshold` of the Safe.
- `enable_module <address>`: Enable module `address`
- `disable_module <address>`: Disable module `address`
- `change_fallback_handler <address>`: Updates the fallback handler to be `address`. Supported by Safes with `version >= v1.1.0`. **WARNING: DON'T USE
  THIS IF YOU DON'T KNOW WHAT YOU ARE DOING. ALL YOUR FUNDS COULD BE LOST**
- `change_guard <address>`: Updates the guard to be `address`. Supported by Safes with `version >= v1.3.0`. **WARNING: DON'T USE
  THIS IF YOU DON'T KNOW WHAT YOU ARE DOING. ALL YOUR FUNDS COULD BE LOST**
- `change_master_copy <address>`: Updates the master copy to be `address`. It's used to update the Safe. **WARNING: DON'T USE
  THIS IF YOU DON'T KNOW WHAT YOU ARE DOING. ALL YOUR FUNDS COULD BE LOST**
- `update`: Updates the Safe to the latest version (if you are on a known network like `Goerli` or `Mainnet`).
- `update_to_l2 <address>`: Updates a v1.1.1/v1.3.0/v1.4.1 non L2 Safe to a L2 Safe supported by Safe Wallet UI.
  The migration contract address needs to be provided.
  It can be found [here](https://github.com/safe-global/safe-contracts/blob/main/contracts/libraries/SafeToL2Migration.sol).
  Nonce for the Safe must be 0 and supported versions are v1.1.1, v1.3.0 and v1.4.1.
  **WARNING: DON'T USE THIS IF YOU DON'T KNOW WHAT YOU ARE DOING. ALL YOUR FUNDS COULD BE LOST**

### Operations only in tx-service mode

- `balances`: Returns a list of balances for ERC20 tokens and ether.
- `history`: History of multisig transactions (including pending).
- `execute-tx <safe-tx-hash>`: Execute a pending tx with enough signatures.
- `sign-tx <safe-tx-hash>`: Sign a tx with the loaded owners for the provided `SafeTxHash`.
- `sign_message [--eip191_message <str>] [--eip712_path <file-path>]`: sign the provided string message provided by standard input or the `EIP712` provided by file.
- `batch-txs <safe-nonce> <safe-tx-hash> [ <safe-tx-hash> ... ]`: Batch transactions into one Multisig
  Transaction using the provided `safe-nonce`. **Any safe-tx can be used**: transactions from other Safes, transactions
  already executed, transactions pending for execution... Only limitation is that
- **transactions from other networks cannot be used**. Batching order will follow the same order of the
  `safe-tx-hashes` provided.
- `get_delegates`: Returns a list of **delegates** for the Safe. A **delegate** can be used when you **trust an address to post transactions to the tx-service on your behalf**. If a transaction is not trusted (posted to the service not signed by a delegate or an owner of the Safe) it will be stored in the service but not shown in the UI or mobile applications.
- `add_delegate <address> <label> <owner-address>`: Adds a new delegate `address` for the `owner` of the Safe.
- `remove_delegate <address> <owner-address>`: Removes a delegate `address` from the Safe.
- `remove_proposed_transaction <safe_tx_hsh>`: Removes a proposed non executed transaction with the signature of the owner that proposed the transaction.
- `drain <address>`: Sends all Ether and ERC20 funds to the provided account. **WARNING: DON'T USE THIS IF YOU DON'T KNOW WHAT YOU ARE DOING. ALL YOUR FUNDS COULD BE LOST**

If the information in the information bar is outdated or there's any problem you can force the `safe-cli` to update the information about the Safe using:

```bash
> refresh
```

## Demos

### Creating a Safe

For this demo, `PRIVATE_KEY` environment variable was set to an _EOA_ private key.

[![asciicast](https://asciinema.org/a/0jdHGLVRrkS9URxPoZ8ZJ7W2C.svg)](https://asciinema.org/a/0jdHGLVRrkS9URxPoZ8ZJ7W2C)

### Sending Ether using a Trezor hardware wallet

[![asciicast](https://asciinema.org/a/9BrQKYQRXbysmEL8rw1jDWZhn.svg)](https://asciinema.org/a/9BrQKYQRXbysmEL8rw1jDWZhn)

### Create a remove owner transaction in the Transaction Service

[![asciicast](https://asciinema.org/a/oV5UbXW2g1VZo2yKDQIxi0jYb.svg)](https://asciinema.org/a/oV5UbXW2g1VZo2yKDQIxi0jYb)

## Use custom contracts

**Safe-cli** comes with the official deterministic Safe contract addresses deployed on multiple chains configured by default. If you want to use your own you can edit the file `safe_cli/safe_addresses.py`

Be careful when modifying these addresses, the funds in a Safe can get stuck if an invalid address it's used when updating to an invalid Safe Master Copy.

## Recovery Safe Deployment Guide

This guide will walk you through the process of recreating a Safe with the same address on the desired network, in case you sent funds to your Safe address in an incorrect chain.

**Note: It's not always posible to recover a Safe, [check this link](https://help.safe.global/en/articles/40812-i-sent-assets-to-a-safe-address-on-the-wrong-network-any-chance-to-recover)**

### Recreate Safe 1.3.0 or 1.1.1

To recreate a Safe (version 1.3.0 or 1.1.1), you'll need the following essential data::

- The `Singleton` address
- The `ProxyFactory` address
- The `FallbackHandler` address
- The `Owners` addresses with which Safe was created
- The `SaltNonce` value
- The `Threshold` value
- RPC node provider for the target chain.
- The private-key of deployer address

The necessary addresses can be collected from [safe-deployments](https://github.com/safe-global/safe-deployments/tree/main/src/assets) and the salt nonce from the **Safe creation transaction** in a block explorer.

**WARNING**: Ensure that the `Singleton`, `ProxyFactory`, and `FallbackHandler` are deployed in the target chain in the same addresses as the origin chain.

To recreate the Safe is necessary execute `safe-creator` as follows:

```commandline
safe-creator --owners <owners-addresses> --safe-contract <singleton-address>
--callback-handler <fallback-handler-address> --proxy-factory <proxy-factory-address>
--threshold <threshold-value> --salt-nonce <salt-nonce-value> <url-rpc-node>  <deployer-private-key>
```

The Safe should have been successfully recreated with the same address on the target chain. If not, double-check the data collected from the transaction and ensure that all the necessary contracts are deployed in the chain.

### Migrate a Safe from Non L2 to L2

If you've recreated a Safe from a L1 network (like mainnet) on a L2 network, our services will not be able to index them as for L1 we use trace based indexing and for L2 events indexing, and L1 Safe singleton does not emmit events.
To address this, you'll need to update it to the L2 singleton with command `update_to_l2` or consider transferring the funds to a new Safe on L2 that you control with `drain` command.
For detailed instructions on running these commands, please refer to the [Common operations](#common-operations) section for more information.

## Safe{Core} API/Protocol

- [Safe Infrastructure](https://github.com/safe-global/safe-infrastructure)
- [Safe Transaction Service](https://github.com/safe-global/safe-transaction-service)
- [Safe Smart Account](https://github.com/safe-global/safe-smart-account)
- [Safe Smart Account deployment info and addreses](https://github.com/safe-global/safe-deployments/tree/main/src/assets)

## Setting up for developing

If you miss something and want to send us a PR:

```bash
git clone https://github.com/safe-global/safe-cli.git
cd safe-cli
stat venv 2>/dev/null || python3 -m venv venv
source venv/bin/activate && pip install -r requirements-dev.txt
pre-commit install -f
```

## Contributors

- [Pedro Arias Ruiz](https://github.com/AsiganTheSunk)
- [Uxío Fuentefría](https://github.com/uxio0)
- [Moisés Fernández](https://github.com/moisses89)
