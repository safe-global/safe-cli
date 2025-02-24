import argparse
import functools

from prompt_toolkit import HTML, print_formatted_text
from prompt_toolkit.formatted_text import html
from safe_eth.safe.api import SafeAPIException
from safe_eth.util.util import to_0x_hex_str

from .argparse_validators import (
    check_ethereum_address,
    check_hex_str,
    check_keccak256_hash,
)
from .operators import SafeServiceNotAvailable
from .operators.exceptions import (
    AccountNotLoadedException,
    ExistingOwnerException,
    FallbackHandlerNotSupportedException,
    HardwareWalletException,
    HashAlreadyApproved,
    InvalidMasterCopyException,
    InvalidMigrationContractException,
    InvalidNonceException,
    NonExistingOwnerException,
    NotEnoughEtherToSend,
    NotEnoughSignatures,
    NotEnoughTokenToSend,
    SafeAlreadyUpdatedException,
    SafeCliTerminationException,
    SafeOperatorException,
    SafeVersionNotSupportedException,
    SameFallbackHandlerException,
    SameMasterCopyException,
    SenderRequiredException,
    ThresholdLimitException,
)
from .operators.safe_operator import SafeOperator
from .safe_completer_constants import meta, safe_commands_arguments


def safe_exception(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except SafeAPIException as e:
            if e.args:
                print_formatted_text(HTML(f"<b><ansired>{e.args[0]}</ansired></b>"))
        except AccountNotLoadedException as e:
            print_formatted_text(
                HTML(f"<ansired>Account {e.args[0]} is not loaded</ansired>")
            )
        except NotEnoughSignatures as e:
            print_formatted_text(
                HTML(
                    f"<ansired>Cannot find enough owners to sign. {e.args[0]} missing</ansired>"
                )
            )
        except SenderRequiredException:
            print_formatted_text(
                HTML("<ansired>Please load a default sender</ansired>")
            )
        except ExistingOwnerException as e:
            print_formatted_text(
                HTML(
                    f"<ansired>Owner {e.args[0]} is already an owner of the Safe"
                    f"</ansired>"
                )
            )
        except NonExistingOwnerException as e:
            print_formatted_text(
                HTML(
                    f"<ansired>Owner {e.args[0]} is not an owner of the Safe"
                    f"</ansired>"
                )
            )
        except HashAlreadyApproved as e:
            print_formatted_text(
                HTML(
                    f"<ansired>Transaction with safe-tx-hash {to_0x_hex_str(e.args[0])} has already been approved by "
                    f"owner {e.args[1]}</ansired>"
                )
            )
        except ThresholdLimitException:
            print_formatted_text(
                HTML(
                    "<ansired>Having less owners than threshold is not allowed"
                    "</ansired>"
                )
            )
        except SameFallbackHandlerException as e:
            print_formatted_text(
                HTML(
                    f"<ansired>Fallback handler {e.args[0]} is the current one</ansired>"
                )
            )
        except FallbackHandlerNotSupportedException:
            print_formatted_text(
                HTML(
                    "<ansired>Fallback handler is not supported for your Safe, "
                    "you need to <b>update</b> first</ansired>"
                )
            )
        except SameMasterCopyException as e:
            print_formatted_text(
                HTML(f"<ansired>Master Copy {e.args[0]} is the current one</ansired>")
            )
        except InvalidMasterCopyException as e:
            print_formatted_text(
                HTML(f"<ansired>Master Copy {e.args[0]} is not valid</ansired>")
            )
        except InvalidMigrationContractException as e:
            print_formatted_text(HTML(f"<ansired>{e.args[0]}</ansired>"))
        except InvalidNonceException as e:
            print_formatted_text(HTML(f"<ansired>{e.args[0]}</ansired>"))
        except SafeAlreadyUpdatedException:
            print_formatted_text(HTML("<ansired>Safe is already updated</ansired>"))
        except SafeVersionNotSupportedException as e:
            print_formatted_text(HTML(f"<ansired>{e.args[0]}</ansired>"))
        except (NotEnoughEtherToSend, NotEnoughTokenToSend) as e:
            print_formatted_text(
                HTML(
                    f"<ansired>Cannot find enough to send. Current balance is {e.args[0]}"
                    f"</ansired>"
                )
            )
        except SafeServiceNotAvailable as e:
            print_formatted_text(
                HTML(
                    f"<ansired>Service not available for network {e.args[0]}</ansired>"
                )
            )
        except HardwareWalletException as e:
            print_formatted_text(
                HTML(f"<ansired>HwDevice exception: {e.args[0]}</ansired>")
            )
        except SafeOperatorException as e:
            print_formatted_text(HTML(f"<ansired>{e.args[0]}</ansired>"))

    return wrapper


class PromptParser:
    def __init__(self, safe_operator: SafeOperator):
        self.mode_parser = argparse.ArgumentParser(prog="")
        self.safe_operator = safe_operator
        self.prompt_parser = build_prompt_parser(safe_operator)

    def process_command(self, command: str):
        args = self.prompt_parser.parse_args(command.split())
        return args.func(args)


def build_prompt_parser(safe_operator: SafeOperator) -> argparse.ArgumentParser:
    """
    Returns an ArgParse capable of decoding and executing the Safe commands
    :param safe_operator:
    :return:
    """
    prompt_parser = argparse.ArgumentParser(prog="")
    subparsers = prompt_parser.add_subparsers()

    @safe_exception
    def show_cli_owners(args):
        safe_operator.show_cli_owners()

    @safe_exception
    def load_cli_owners_from_words(args):
        safe_operator.load_cli_owners_from_words(args.words)

    @safe_exception
    def load_cli_owners(args):
        safe_operator.load_cli_owners(args.keys)

    @safe_exception
    def load_ledger_cli_owners(args):
        safe_operator.load_ledger_cli_owners(
            derivation_path=args.derivation_path, legacy_account=args.legacy_accounts
        )

    @safe_exception
    def load_trezor_cli_owners(args):
        safe_operator.load_trezor_cli_owners(
            derivation_path=args.derivation_path, legacy_account=args.legacy_accounts
        )

    @safe_exception
    def unload_cli_owners(args):
        safe_operator.unload_cli_owners(args.addresses)

    @safe_exception
    def approve_hash(args):
        safe_operator.approve_hash(args.hash_to_approve, args.sender)

    @safe_exception
    def sign_message(args):
        safe_operator.sign_message(args.eip712_path)

    @safe_exception
    def confirm_message(args):
        safe_operator.confirm_message(args.safe_message_hash, args.sender)

    @safe_exception
    def add_owner(args):
        safe_operator.add_owner(args.address, threshold=args.threshold)

    @safe_exception
    def remove_owner(args):
        safe_operator.remove_owner(args.address, threshold=args.threshold)

    @safe_exception
    def change_fallback_handler(args):
        safe_operator.change_fallback_handler(args.address)

    @safe_exception
    def change_guard(args):
        safe_operator.change_guard(args.address)

    @safe_exception
    def change_master_copy(args):
        safe_operator.change_master_copy(args.address)

    @safe_exception
    def change_threshold(args):
        safe_operator.change_threshold(args.threshold)

    @safe_exception
    def send_custom(args):
        safe_operator.send_custom(
            args.to,
            args.value,
            args.data,
            safe_nonce=args.safe_nonce,
            delegate_call=args.delegate,
        )

    @safe_exception
    def send_ether(args):
        safe_operator.send_ether(args.to, args.value, safe_nonce=args.safe_nonce)

    @safe_exception
    def send_erc20(args):
        safe_operator.send_erc20(
            args.to, args.token_address, args.amount, safe_nonce=args.safe_nonce
        )

    @safe_exception
    def send_erc721(args):
        safe_operator.send_erc721(
            args.to, args.token_address, args.token_id, safe_nonce=args.safe_nonce
        )

    @safe_exception
    def drain(args):
        safe_operator.drain(args.to)

    @safe_exception
    def get_threshold(args):
        safe_operator.get_threshold()

    @safe_exception
    def get_nonce(args):
        safe_operator.get_nonce()

    @safe_exception
    def get_owners(args):
        safe_operator.get_owners()

    @safe_exception
    def enable_module(args):
        safe_operator.enable_module(args.address)

    @safe_exception
    def disable_module(args):
        safe_operator.disable_module(args.address)

    @safe_exception
    def update_version(args):
        safe_operator.update_version()

    @safe_exception
    def update_version_to_l2(args):
        safe_operator.update_version_to_l2(args.migration_contract)

    @safe_exception
    def get_info(args):
        safe_operator.print_info()

    @safe_exception
    def get_refresh(args):
        safe_operator.refresh_safe_cli_info()

    @safe_exception
    def get_balances(args):
        safe_operator.get_balances()

    @safe_exception
    def get_history(args):
        safe_operator.get_transaction_history()

    @safe_exception
    def sign_tx(args):
        safe_operator.submit_signatures(args.safe_tx_hash)

    @safe_exception
    def batch_txs(args):
        safe_operator.batch_txs(args.safe_nonce, args.safe_tx_hashes)

    @safe_exception
    def execute_tx(args):
        safe_operator.execute_tx(args.safe_tx_hash)

    @safe_exception
    def get_delegates(args):
        safe_operator.get_delegates()

    @safe_exception
    def add_delegate(args):
        safe_operator.add_delegate(args.address, args.label, args.signer)

    @safe_exception
    def remove_delegate(args):
        safe_operator.remove_delegate(args.address, args.signer)

    @safe_exception
    def remove_proposed_transaction(args):
        safe_operator.remove_proposed_transaction(args.safe_tx_hash)

    def list_commands(args):
        print_formatted_text(
            HTML("<b>The following commands can be used:</b>"), end="\n\n"
        )
        for key in sorted(safe_commands_arguments.keys()):
            print_formatted_text(
                HTML(
                    f"<b>{key} {html.html_escape(safe_commands_arguments.get(key))}</b>"
                )
            )
            print_formatted_text(HTML("&#9;"), meta.get(key, ""))
        print_formatted_text(
            HTML("\nUse the <b>tab key</b> to show options in interactive mode.")
        )

    def terminate_cli(args):
        raise SafeCliTerminationException()

    # Cli owners
    parser_show_cli_owners = subparsers.add_parser("show_cli_owners")
    parser_show_cli_owners.set_defaults(func=show_cli_owners)

    parser_load_cli_owners_from_words = subparsers.add_parser(
        "load_cli_owners_from_words"
    )
    parser_load_cli_owners_from_words.add_argument("words", type=str, nargs="+")
    parser_load_cli_owners_from_words.set_defaults(func=load_cli_owners_from_words)

    parser_load_cli_owners = subparsers.add_parser("load_cli_owners")
    parser_load_cli_owners.add_argument("keys", type=str, nargs="+")
    parser_load_cli_owners.set_defaults(func=load_cli_owners)

    parser_load_ledger_cli_owners = subparsers.add_parser("load_ledger_cli_owners")
    parser_load_ledger_cli_owners.add_argument(
        "--derivation-path",
        type=str,
        help="Load address for the provided derivation path",
    )
    parser_load_ledger_cli_owners.add_argument(
        "--legacy-accounts",
        action="store_true",
        help="Search for legacy accounts",
    )
    parser_load_ledger_cli_owners.set_defaults(func=load_ledger_cli_owners)

    parser_load_trezor_cli_owners = subparsers.add_parser("load_trezor_cli_owners")
    parser_load_trezor_cli_owners.add_argument(
        "--derivation-path",
        type=str,
        help="Load address for the provided derivation path",
    )
    parser_load_trezor_cli_owners.add_argument(
        "--legacy-accounts",
        action="store_true",
        help="Search for legacy accounts",
    )
    parser_load_trezor_cli_owners.set_defaults(func=load_trezor_cli_owners)

    parser_unload_cli_owners = subparsers.add_parser("unload_cli_owners")
    parser_unload_cli_owners.add_argument(
        "addresses", type=check_ethereum_address, nargs="+"
    )
    parser_unload_cli_owners.set_defaults(func=unload_cli_owners)

    # Change threshold
    parser_change_threshold = subparsers.add_parser("change_threshold")
    parser_change_threshold.add_argument("threshold", type=int)
    parser_change_threshold.set_defaults(func=change_threshold)

    # Approve hash
    parser_approve_hash = subparsers.add_parser("approve_hash")
    parser_approve_hash.add_argument("hash_to_approve", type=check_keccak256_hash)
    parser_approve_hash.add_argument("sender", type=check_ethereum_address)
    parser_approve_hash.set_defaults(func=approve_hash)

    # Sign message
    parser_sign_message = subparsers.add_parser("sign_message")
    group = parser_sign_message.add_mutually_exclusive_group(required=True)
    group.add_argument("--eip191_message", action="store_true")
    group.add_argument("--eip712_path", type=str)
    parser_sign_message.set_defaults(func=sign_message)

    # Confirm message
    parser_confirm_message = subparsers.add_parser("confirm_message")
    parser_confirm_message.add_argument("safe_message_hash", type=check_keccak256_hash)
    parser_confirm_message.add_argument("sender", type=check_ethereum_address)
    parser_confirm_message.set_defaults(func=confirm_message)

    # Add owner
    parser_add_owner = subparsers.add_parser("add_owner")
    parser_add_owner.add_argument("address", type=check_ethereum_address)
    parser_add_owner.add_argument("--threshold", type=int, default=None)
    parser_add_owner.set_defaults(func=add_owner)

    # Remove owner
    parser_remove_owner = subparsers.add_parser("remove_owner")
    parser_remove_owner.add_argument("address", type=check_ethereum_address)
    parser_remove_owner.add_argument("--threshold", type=int, default=None)
    parser_remove_owner.set_defaults(func=remove_owner)

    # Change FallbackHandler
    parser_change_fallback_handler = subparsers.add_parser("change_fallback_handler")
    parser_change_fallback_handler.add_argument("address", type=check_ethereum_address)
    parser_change_fallback_handler.set_defaults(func=change_fallback_handler)

    # Change Guard
    parser_change_guard = subparsers.add_parser("change_guard")
    parser_change_guard.add_argument("address", type=check_ethereum_address)
    parser_change_guard.set_defaults(func=change_guard)

    # Change MasterCopy
    parser_change_master_copy = subparsers.add_parser("change_master_copy")
    parser_change_master_copy.add_argument("address", type=check_ethereum_address)
    parser_change_master_copy.set_defaults(func=change_master_copy)

    # Update Safe to last version
    parser_update_version = subparsers.add_parser("update")
    parser_update_version.set_defaults(func=update_version)

    # Update non L2 Safe to L2 Safe
    parser_update_version_to_l2 = subparsers.add_parser("update_version_to_l2")
    parser_update_version_to_l2.add_argument(
        "migration_contract", type=check_ethereum_address
    )
    parser_update_version_to_l2.set_defaults(func=update_version_to_l2)

    # Send custom/ether/erc20/erc721
    parser_send_custom = subparsers.add_parser("send_custom")
    parser_send_ether = subparsers.add_parser("send_ether")
    parser_send_erc20 = subparsers.add_parser("send_erc20")
    parser_send_erc721 = subparsers.add_parser("send_erc721")
    parser_send_custom.set_defaults(func=send_custom)
    parser_send_ether.set_defaults(func=send_ether)
    parser_send_erc20.set_defaults(func=send_erc20)
    parser_send_erc721.set_defaults(func=send_erc721)
    # They have some common arguments
    for parser in (
        parser_send_custom,
        parser_send_ether,
        parser_send_erc20,
        parser_send_erc721,
    ):
        parser.add_argument(
            "--safe-nonce",
            type=int,
            help="Use custom safe nonce instead of "
            "the one for last executed SafeTx + 1",
        )

    # To/value is common for send custom and send ether
    for parser in (parser_send_custom, parser_send_ether):
        parser.add_argument("to", type=check_ethereum_address)
        parser.add_argument("value", type=int)

    parser_send_custom.add_argument("data", type=check_hex_str)
    parser_send_custom.add_argument(
        "--delegate", action="store_true", help="Use DELEGATE_CALL. By default use CALL"
    )

    # Send erc20/721 have common arguments
    for parser in (parser_send_erc20, parser_send_erc721):
        parser.add_argument("to", type=check_ethereum_address)
        parser.add_argument("token_address", type=check_ethereum_address)

    parser_send_erc20.add_argument("amount", type=int)
    parser_send_erc721.add_argument("token_id", type=int)

    # Drain only needs receiver account
    parser_drain = subparsers.add_parser("drain")
    parser_drain.set_defaults(func=drain)
    parser_drain.add_argument("to", type=check_ethereum_address)

    # Retrieve threshold, nonce or owners
    parser_get_threshold = subparsers.add_parser("get_threshold")
    parser_get_threshold.set_defaults(func=get_threshold)

    parser_get_nonce = subparsers.add_parser("get_nonce")
    parser_get_nonce.set_defaults(func=get_nonce)

    parser_get_owners = subparsers.add_parser("get_owners")
    parser_get_owners.set_defaults(func=get_owners)

    # Enable and disable modules
    parser_enable_module = subparsers.add_parser("enable_module")
    parser_enable_module.add_argument("address", type=check_ethereum_address)
    parser_enable_module.set_defaults(func=enable_module)

    parser_disable_module = subparsers.add_parser("disable_module")
    parser_disable_module.add_argument("address", type=check_ethereum_address)
    parser_disable_module.set_defaults(func=disable_module)

    # Info and refresh
    parser_info = subparsers.add_parser("info")
    parser_info.set_defaults(func=get_info)

    parser_refresh = subparsers.add_parser("refresh")
    parser_refresh.set_defaults(func=get_refresh)

    # Tx-Service
    # TODO Use subcommands
    parser_tx_service = subparsers.add_parser("balances")
    parser_tx_service.set_defaults(func=get_balances)

    parser_tx_service = subparsers.add_parser("history")
    parser_tx_service.set_defaults(func=get_history)

    parser_tx_service = subparsers.add_parser("sign-tx")
    parser_tx_service.set_defaults(func=sign_tx)
    parser_tx_service.add_argument("safe_tx_hash", type=check_keccak256_hash)

    parser_tx_service = subparsers.add_parser("batch-txs")
    parser_tx_service.set_defaults(func=batch_txs)
    parser_tx_service.add_argument("safe_nonce", type=int)
    parser_tx_service.add_argument(
        "safe_tx_hashes", type=check_keccak256_hash, nargs="+"
    )

    parser_tx_service = subparsers.add_parser("execute-tx")
    parser_tx_service.set_defaults(func=execute_tx)
    parser_tx_service.add_argument("safe_tx_hash", type=check_keccak256_hash)

    # List delegates
    parser_delegates = subparsers.add_parser("get_delegates")
    parser_delegates.set_defaults(func=get_delegates)

    # Add delegate
    parser_add_delegate = subparsers.add_parser("add_delegate")
    parser_add_delegate.set_defaults(func=add_delegate)
    parser_add_delegate.add_argument("address", type=check_ethereum_address)
    parser_add_delegate.add_argument("label", type=str)
    parser_add_delegate.add_argument("signer", type=check_ethereum_address)

    # Remove delegate
    parser_remove_delegate = subparsers.add_parser("remove_delegate")
    parser_remove_delegate.set_defaults(func=remove_delegate)
    parser_remove_delegate.add_argument("address", type=check_ethereum_address)
    parser_remove_delegate.add_argument("signer", type=check_ethereum_address)

    # Remove not executed proposed transaction
    parser_remove_proposed_transaction = subparsers.add_parser(
        "remove_proposed_transaction"
    )
    parser_remove_proposed_transaction.set_defaults(func=remove_proposed_transaction)
    parser_remove_proposed_transaction.add_argument(
        "safe_tx_hash", type=check_keccak256_hash
    )

    # List all command options
    parser_help = subparsers.add_parser("help")
    parser_help.set_defaults(func=list_commands)

    # Terminate safe cli
    parser_exit = subparsers.add_parser("exit")
    parser_exit.set_defaults(func=terminate_cli)

    return prompt_parser
