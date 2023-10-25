import functools

from ledgereth.exceptions import (
    LedgerAppNotOpened,
    LedgerCancel,
    LedgerLocked,
    LedgerNotFound,
)

from safe_cli.operators.safe_operator import HwDeviceException


def hw_account_exception(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except LedgerNotFound as e:
            raise HwDeviceException(e.message)
        except LedgerLocked as e:
            raise HwDeviceException(e.message)
        except LedgerAppNotOpened as e:
            raise HwDeviceException(e.message)
        except LedgerCancel as e:
            raise HwDeviceException(e.message)
        except BaseException as e:
            if "Error while writing" in e.args:
                raise HwDeviceException("Ledger error writting, restart safe-cli")
            raise e

    return wrapper
