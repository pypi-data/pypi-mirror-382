"""Custom exceptions for check_bitdefender."""


class CheckbitdefenderError(Exception):
    """Base exception for check_bitdefender."""

    pass


class ConfigurationError(CheckbitdefenderError):
    """Raised when there's a configuration error."""

    pass


class AuthenticationError(CheckbitdefenderError):
    """Raised when there's an authentication error."""

    pass


class DefenderAPIError(CheckbitdefenderError):
    """Raised when there's an error with the Defender API."""

    pass


class ValidationError(CheckbitdefenderError):
    """Raised when there's a validation error."""

    pass
