import functools

from trezorlib.exceptions import (
    Cancelled,
    OutdatedFirmwareError,
    PassphraseError,
    PinException,
    TrezorException,
    TrezorFailure,
)
from trezorlib.transport import DeviceIsBusy, TransportException

from ..exceptions import HardwareWalletException
from .exceptions import InvalidDerivationPath


def raise_trezor_exception_as_hw_wallet_exception(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except TrezorFailure as e:
            raise HardwareWalletException(e.message) from e
        except OutdatedFirmwareError:
            raise HardwareWalletException(
                "Trezor firmware version is not supported"
            ) from None
        except PinException:
            raise HardwareWalletException("Wrong PIN") from None
        except PassphraseError as e:
            raise HardwareWalletException(f"Trezor passphrase error: {e}") from e
        except Cancelled:
            raise HardwareWalletException("Trezor operation was cancelled") from None
        # DeviceIsBusy is a TransportException, so it goes first
        except DeviceIsBusy:
            raise HardwareWalletException(
                "Trezor is in use by another program, close Trezor Suite and try again"
            ) from None
        except TransportException:
            raise HardwareWalletException("Trezor device is not connected") from None
        except InvalidDerivationPath as e:
            raise HardwareWalletException(e.message) from e
        except TrezorException as e:
            raise HardwareWalletException(f"Trezor error: {e}") from e

    return wrapper
