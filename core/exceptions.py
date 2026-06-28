class KaomyError(Exception):
    """
    Base exception for all Kaomy errors.
    """
    pass


class ProviderError(KaomyError):
    """
    Raised when an external provider fails.

    Examples:
        - login failure
        - HTTP error
        - invalid provider response
        - unavailable service
    """
    pass


class CacheError(KaomyError):
    """
    Raised when Kaomy cannot read, write, or delete cache data.
    """
    pass


class CollectorError(KaomyError):
    """
    Raised when a collector cannot orchestrate its workflow correctly.
    """
    pass


class SensorError(KaomyError):
    """
    Raised when Home Assistant sensor publishing fails.
    """
    pass
