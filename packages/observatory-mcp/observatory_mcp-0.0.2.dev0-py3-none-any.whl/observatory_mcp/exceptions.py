"""Custom exceptions for Observatory SDK."""


class ObservatoryError(Exception):
    """Base exception for all Observatory SDK errors."""

    pass


class ConfigurationError(ObservatoryError):
    """Raised when SDK configuration is invalid."""

    pass


class AuthenticationError(ObservatoryError):
    """Raised when API authentication fails."""

    pass


class ConnectionError(ObservatoryError):
    """Raised when connection to Observatory backend fails."""

    pass


class SamplingError(ObservatoryError):
    """Raised when sampling logic encounters an error."""

    pass


class PrivacyError(ObservatoryError):
    """Raised when privacy operations fail."""

    pass
