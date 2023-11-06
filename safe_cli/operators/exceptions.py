class SafeOperatorException(Exception):
    pass


class ExistingOwnerException(SafeOperatorException):
    pass


class NonExistingOwnerException(SafeOperatorException):
    pass


class HashAlreadyApproved(SafeOperatorException):
    pass


class ThresholdLimitException(SafeOperatorException):
    pass


class SameFallbackHandlerException(SafeOperatorException):
    pass


class InvalidFallbackHandlerException(SafeOperatorException):
    pass


class FallbackHandlerNotSupportedException(SafeOperatorException):
    pass


class SameGuardException(SafeOperatorException):
    pass


class InvalidGuardException(SafeOperatorException):
    pass


class GuardNotSupportedException(SafeOperatorException):
    pass


class SameMasterCopyException(SafeOperatorException):
    pass


class SafeAlreadyUpdatedException(SafeOperatorException):
    pass


class SafeVersionNotSupportedException(SafeOperatorException):
    pass


class UpdateAddressesNotValid(SafeOperatorException):
    pass


class SenderRequiredException(SafeOperatorException):
    pass


class AccountNotLoadedException(SafeOperatorException):
    pass


class NotEnoughSignatures(SafeOperatorException):
    pass


class InvalidMasterCopyException(SafeOperatorException):
    pass


class InvalidMigrationContractException(SafeOperatorException):
    pass


class InvalidNonceException(SafeOperatorException):
    pass


class NotEnoughEtherToSend(SafeOperatorException):
    pass


class NotEnoughTokenToSend(SafeOperatorException):
    pass


class SafeServiceNotAvailable(SafeOperatorException):
    pass


class HardwareWalletException(SafeOperatorException):
    pass
