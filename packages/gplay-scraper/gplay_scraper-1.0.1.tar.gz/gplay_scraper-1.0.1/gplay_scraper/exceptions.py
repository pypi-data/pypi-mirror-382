"""Custom exceptions for GPlay Scraper."""


class GPlayScraperError(Exception):
    """Base exception for GPlay Scraper."""
    pass


class InvalidAppIdError(GPlayScraperError):
    """Raised when an invalid app ID is provided."""
    pass


class AppNotFoundError(GPlayScraperError):
    """Raised when an app is not found on the Play Store."""
    pass


class RateLimitError(GPlayScraperError):
    """Raised when rate limit is exceeded."""
    pass


class NetworkError(GPlayScraperError):
    """Raised when network-related errors occur."""
    pass


class DataParsingError(GPlayScraperError):
    """Raised when data parsing fails."""
    pass