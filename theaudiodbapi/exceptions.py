"""Exceptions for the Gecaching API."""

class TheAudioDBApiError(Exception):
    """Generic TheAudioDBApi exception."""


class TheAudioDBApiConnectionError(TheAudioDBApiError):
    """TheAudioDBApi connection exception."""


class TheAudioDBApiConnectionTimeoutError(TheAudioDBApiConnectionError):
    """TheAudioDBApi connection timeout exception."""


class TheAudioDBApiRateLimitError(TheAudioDBApiConnectionError):
    """TheAudioDBApi Rate Limit exception."""
    