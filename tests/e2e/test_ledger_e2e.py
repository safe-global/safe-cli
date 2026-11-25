"""
The Ledger wallet against the real Ethereum app in the Speculos emulator:
list accounts, load the device as owner and sender of a Safe, sign and execute
a SafeTx and sign a Safe message. Buttons are pressed through the emulator
REST API, and the screens it showed are asserted at the end.

    uv run pytest -m e2e -v
"""

import pytest

pytest.importorskip("ledgereth")
from safe_eth.eth.eip712 import eip712_encode
from safe_eth.eth.utils import fast_to_checksum_address

from safe_cli.operators.hw_wallets.hw_wallet_manager import HwWalletType
from safe_cli.operators.hw_wallets.ledger_wallet import LedgerWallet

from .helpers import run_cli_flow

pytestmark = pytest.mark.e2e
# Speculos seed "abandon … about" at 44'/60'/0'/0/0
LEDGER_PATH = "44'/60'/0'/0/0"
LEDGER_ADDRESS = fast_to_checksum_address("0x9858EfFD232B4033E47d90003D41EC34EcaEda94")


def test_ledger_signs_and_executes(
    speculos, client, deployer, safe_contracts, monkeypatch
):
    signed_typed_data = []
    sign_typed_data = LedgerWallet.sign_typed_data

    def record_sign_typed_data(self, typed_data):
        signed_typed_data.append(typed_data)
        return sign_typed_data(self, typed_data)

    monkeypatch.setattr(LedgerWallet, "sign_typed_data", record_sign_typed_data)
    with speculos.approve_everything() as approver:
        run_cli_flow(
            client,
            deployer,
            safe_contracts,
            HwWalletType.LEDGER,
            "44'/60'/{i}'/0/0",
            LEDGER_PATH,
            LEDGER_ADDRESS,
            lambda safe_operator: safe_operator.load_ledger_cli_owners(
                derivation_path=LEDGER_PATH
            ),
        )

    # The device showed the hashes the CLI prints for the user to compare
    assert approver.saw("Review typed"), approver.seen
    assert approver.saw("Domain hash"), approver.seen
    assert approver.saw("Message hash"), approver.seen
    assert approver.saw("Review transaction"), approver.seen
    assert approver.saw("Sign message"), approver.seen
    [typed_data] = signed_typed_data
    _, domain_hash, message_hash = eip712_encode(typed_data)
    shown = approver.shown().lower().replace("0x", "")
    assert domain_hash.hex()[:12] in shown
    assert message_hash.hex()[:12] in shown
