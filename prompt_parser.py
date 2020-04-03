import argparse

from safe_operator import SafeOperator
from web3 import Web3


def check_ethereum_address(address: str) -> bool:
    if not Web3.isChecksumAddress(address):
        raise argparse.ArgumentTypeError(f'{address} is not a valid checksummed ethereum address')
    return address


def get_prompt_parser(safe_operator: SafeOperator) -> argparse.ArgumentParser:
    prompt_parser = argparse.ArgumentParser(prog='')
    subparsers = prompt_parser.add_subparsers()

    def show_cli_owners(args):
        safe_operator.show_cli_owners()

    def load_cli_owners(args):
        safe_operator.load_cli_owners(args.keys)

    def unload_cli_owners(args):
        safe_operator.unload_cli_owners(args.addresses)

    def add_owner(args):
        safe_operator.add_owner(args.address)

    def remove_owner(args):
        safe_operator.remove_owner(args.address)

    def change_master_copy(args):
        safe_operator.change_master_copy(args.address)

    def change_threshold(args):
        safe_operator.change_threshold(args.threshold)

    def send_ether(args):
        safe_operator.send_ether(args.address, args.value)

    def send_erc20(args):
        safe_operator.send_erc20(args.address, args.token_address, args.value)

    def get_threshold(args):
        safe_operator.get_threshold()

    def get_nonce(args):
        safe_operator.get_nonce()

    def get_owners(args):
        safe_operator.get_owners()

    def enable_module(args):
        safe_operator.enable_module(args.address)

    def disable_module(args):
        safe_operator.disable_module(args.address)

    def get_info(args):
        safe_operator.print_info()

    def get_refresh(args):
        safe_operator.refresh_safe_cli_info()

    def get_history(args):
        safe_operator.get_transaction_history()

    # Cli owners
    parser_show_cli_owners = subparsers.add_parser('show_cli_owners')
    parser_show_cli_owners.set_defaults(func=show_cli_owners)

    parser_load_cli_owners = subparsers.add_parser('load_cli_owners')
    parser_load_cli_owners.add_argument('keys', type=str, nargs='+')
    parser_load_cli_owners.set_defaults(func=load_cli_owners)

    parser_unload_cli_owners = subparsers.add_parser('unload_cli_owners')
    parser_unload_cli_owners.add_argument('addresses', type=check_ethereum_address, nargs='+')
    parser_unload_cli_owners.set_defaults(func=unload_cli_owners)

    # Change threshold
    parser_change_threshold = subparsers.add_parser('change_threshold')
    parser_change_threshold.add_argument('threshold', type=int)
    parser_change_threshold.set_defaults(func=change_threshold)

    # Add owner
    parser_add_owner = subparsers.add_parser('add_owner')
    parser_add_owner.add_argument('address', type=check_ethereum_address)
    parser_add_owner.set_defaults(func=add_owner)

    # Remove owner
    parser_remove_owner = subparsers.add_parser('remove_owner')
    parser_remove_owner.add_argument('address', type=check_ethereum_address)
    parser_remove_owner.set_defaults(func=remove_owner)

    # Change MasterCopy
    parser_change_master_copy = subparsers.add_parser('change_master_copy')
    parser_change_master_copy.add_argument('address', type=check_ethereum_address)
    parser_change_master_copy.set_defaults(func=change_master_copy)

    # Send ether
    parser_send_ether = subparsers.add_parser('send_ether')
    parser_send_ether.add_argument('address', type=check_ethereum_address)
    parser_send_ether.add_argument('value', type=int)
    parser_send_ether.set_defaults(func=send_ether)

    # Send erc20
    parser_send_erc20 = subparsers.add_parser('send_erc20')
    parser_send_erc20.add_argument('address', type=check_ethereum_address)
    parser_send_erc20.add_argument('token_address', type=check_ethereum_address)
    parser_send_erc20.add_argument('value', type=int)
    parser_send_erc20.set_defaults(func=send_erc20)

    # Retrieve threshold, nonce or owners
    parser_get_threshold = subparsers.add_parser('get_threshold')
    parser_get_threshold.set_defaults(func=get_threshold)
    parser_get_nonce = subparsers.add_parser('get_nonce')
    parser_get_nonce.set_defaults(func=get_nonce)
    parser_get_owners = subparsers.add_parser('get_owners')
    parser_get_owners.set_defaults(func=get_owners)

    # Enable and disable modules
    parser_enable_module = subparsers.add_parser('enable_module')
    parser_enable_module.add_argument('address', type=check_ethereum_address)
    parser_enable_module.set_defaults(func=enable_module)
    parser_disable_module = subparsers.add_parser('disable_module')
    parser_disable_module.add_argument('address', type=check_ethereum_address)
    parser_disable_module.set_defaults(func=disable_module)

    # Info and refresh
    parser_info = subparsers.add_parser('info')
    parser_info.set_defaults(func=get_info)
    parser_refresh = subparsers.add_parser('refresh')
    parser_refresh.set_defaults(func=get_refresh)

    # Tx-History
    parser_info = subparsers.add_parser('history')
    parser_info.set_defaults(func=get_history)

    return prompt_parser
