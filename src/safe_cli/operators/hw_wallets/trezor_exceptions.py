import functools

from trezorlib.exceptions import (
    Cancelled,
    DeviceLockedError,
    OutdatedFirmwareError,
    PinException,
    TrezorFailure,
)
from trezorlib.transport import TransportException

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
        except Cancelled:
            raise HardwareWalletException("Trezor operation was cancelled") from None
        except DeviceLockedError:
            raise HardwareWalletException("Trezor device is locked") from None
        except TransportException:
            raise HardwareWalletException("Trezor device is not connected") from None
        except InvalidDerivationPath as e:
            raise HardwareWalletException(e.message) from e

    return wrapper
