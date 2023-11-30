import functools

from trezorlib.exceptions import (
    Cancelled,
    OutdatedFirmwareError,
    PinException,
    TrezorFailure,
)
from trezorlib.transport import TransportException

from safe_cli.operators.exceptions import HardwareWalletException
from safe_cli.operators.hw_accounts.hw_account import InvalidDerivationPath


class UnsupportedHwWalletException(Exception):
    pass


def raise_trezor_exception_as_hw_account_exception(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except TrezorFailure as e:
            raise HardwareWalletException(e.message)
        except OutdatedFirmwareError:
            raise HardwareWalletException("Trezor firmware version is not supported")
        except PinException:
            raise HardwareWalletException("Wrong PIN")
        except Cancelled:
            raise HardwareWalletException("Trezor operation was cancelled")
        except TransportException:
            raise HardwareWalletException("Trezor device is not connected")
        except InvalidDerivationPath as e:
            raise HardwareWalletException(e.message)

    return wrapper
