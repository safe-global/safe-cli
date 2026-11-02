"""
The Trezor wallet against the firmware emulators of trezor-user-env: a Safe 5
(full EIP-712, passphrase typed on the device) and a Model One (hash signing,
PIN and passphrase typed on the host). Local only: the image is 5.5 GB.

    uv run pytest -m e2e_trezor -v
"""

import pytest

pytest.importorskip("trezorlib")
from eth_account import Account

from safe_cli.operators.hw_wallets import trezor_wallet
from safe_cli.operators.hw_wallets.hw_wallet_manager import HwWalletType
from safe_cli.operators.hw_wallets.trezor_wallet import (
    forget_trezor,
    get_trezor_client,
)

from .helpers import run_cli_flow
from .trezor_env import (
    EMULATOR_PATH,
    MNEMONIC,
    Controller,
    TrezorApprover,
    encode_pin,
)

pytestmark = pytest.mark.e2e_trezor
PATH = "44'/60'/0'/0/0"
PIN = "1234"
PASSPHRASE = "hidden"
SAFE_5_FIRMWARE = "2.12.5"


def hidden_wallet_address() -> str:
    """
    :return: address of the test seed with PASSPHRASE at PATH
    """
    Account.enable_unaudited_hdwallet_features()
    return Account.from_mnemonic(
        MNEMONIC, passphrase=PASSPHRASE, account_path="m/" + PATH
    ).address


def load_trezor_owner(safe_operator) -> None:
    safe_operator.load_trezor_cli_owners(derivation_path=PATH)


@pytest.fixture(scope="module")
def controller(trezor_user_env):
    ctl = Controller()
    yield ctl
    ctl.close()


@pytest.fixture
def trezor_prompts(monkeypatch):
    """
    What the user would type on the host, recorded in the yielded list. Every
    test starts with a new connection to the emulator.
    """
    asked = []

    def ask_pin(request) -> str:
        asked.append("pin")
        return encode_pin(PIN)

    def ask_passphrase() -> str:
        asked.append("passphrase")
        return PASSPHRASE

    def ask_pairing_code() -> str:
        raise AssertionError("no pairing expected with the emulator")

    monkeypatch.setenv("TREZOR_PATH", EMULATOR_PATH)
    monkeypatch.setattr(trezor_wallet, "ask_pin", ask_pin)
    monkeypatch.setattr(trezor_wallet, "ask_passphrase", ask_passphrase)
    monkeypatch.setattr(trezor_wallet, "ask_pairing_code", ask_pairing_code)
    forget_trezor()
    yield asked
    forget_trezor()


def test_safe_5_shows_the_typed_data_fields(
    controller, client, deployer, safe_contracts, trezor_prompts
):
    controller.start_emulator("T3T1", SAFE_5_FIRMWARE)
    address = hidden_wallet_address()
    with TrezorApprover(touch=True, passphrase=PASSPHRASE) as approver:
        run_cli_flow(
            client,
            deployer,
            safe_contracts,
            HwWalletType.TREZOR,
            "44'/60'/0'/0/{i}",
            PATH,
            address,
            load_trezor_owner,
        )
    # The passphrase was typed on the device, never asked on the host
    assert trezor_prompts == []
    assert approver.saw("EIP712Domain"), approver.dump()
    assert approver.saw("SafeTx"), approver.dump()
    # The message hash the CLI prints for the user to compare
    assert approver.saw("Confirm message hash"), approver.dump()
    assert approver.saw("Confirm typed data"), approver.dump()
    assert approver.saw("Signing address"), approver.dump()


def test_model_one_signs_hashes_with_host_pin_and_passphrase(
    controller, client, deployer, safe_contracts, trezor_prompts, monkeypatch
):
    versions = controller.firmwares("T1B1")
    version = next((v for v in versions if v[0].isdigit()), versions[0])
    controller.start_emulator("T1B1", version, pin=PIN)

    def sign_typed_data(*args, **kwargs):
        raise AssertionError("the Model One cannot parse typed data")

    monkeypatch.setattr(trezor_wallet, "sign_typed_data", sign_typed_data)
    # A freshly set up emulator is unlocked, lock it so the PIN is asked
    get_trezor_client().lock()
    with TrezorApprover(touch=False):
        run_cli_flow(
            client,
            deployer,
            safe_contracts,
            HwWalletType.TREZOR,
            "44'/60'/0'/0/{i}",
            PATH,
            hidden_wallet_address(),
            load_trezor_owner,
        )
    # Asked once: the session is shared by every derivation path
    assert trezor_prompts == ["pin", "passphrase"]
    assert get_trezor_client().model.internal_name == "T1B1"
