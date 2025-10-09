"""
Exception classes for FastPusher library
"""


class FastPusherError(Exception):
    """Base FastPusher exception class"""

    pass


class ConnectionError(FastPusherError):
    """Server connection error"""

    pass


class AuthenticationError(FastPusherError):
    """Authentication error"""

    pass


class ValidationError(FastPusherError):
    """Data validation error"""

    pass


class RateLimitError(FastPusherError):
    """Rate limit exceeded error"""

    pass


class ChannelNotFoundError(FastPusherError):
    """Channel not found error"""

    pass
