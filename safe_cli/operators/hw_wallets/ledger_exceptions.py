import functools

from ledgereth.exceptions import (
    LedgerAppNotOpened,
    LedgerCancel,
    LedgerLocked,
    LedgerNotFound,
)

from safe_cli.operators.exceptions import HardwareWalletException
from safe_cli.operators.hw_wallets.hw_wallet import InvalidDerivationPath


class UnsupportedHwWalletException(Exception):
    pass


def raise_ledger_exception_as_hw_wallet_exception(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except LedgerNotFound as e:
            raise HardwareWalletException(e.message)
        except LedgerLocked as e:
            raise HardwareWalletException(e.message)
        except LedgerAppNotOpened as e:
            raise HardwareWalletException(e.message)
        except LedgerCancel as e:
            raise HardwareWalletException(e.message)
        except InvalidDerivationPath as e:
            raise HardwareWalletException(e.message)
        except BaseException as e:
            if "Error while writing" in e.args:
                raise HardwareWalletException("Ledger error writting, restart safe-cli")
            raise e

    return wrapper
