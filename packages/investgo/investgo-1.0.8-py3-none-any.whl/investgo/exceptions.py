"""
Custom exceptions for the InvestGo library.

This module defines custom exception classes to provide more specific
error handling and better debugging information.
"""


class InvestGoError(Exception):
    """
    Base exception class for all InvestGo-related errors.

    All other custom exceptions inherit from this base class.
    """
    pass


class APIError(InvestGoError):
    """
    Raised when an API request to Investing.com fails.

    This includes HTTP errors, network timeouts, and invalid responses.
    """
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        if status_code:
            message = f"API Error (HTTP {status_code}): {message}"
        super().__init__(message)


class InvalidParameterError(InvestGoError):
    """
    Raised when invalid parameters are provided to functions.

    This includes invalid date formats, missing required parameters,
    or parameters outside acceptable ranges.
    """
    pass


class NoDataFoundError(InvestGoError):
    """
    Raised when no data is found for the requested parameters.

    This can happen when searching for non-existent tickers or
    requesting data for date ranges with no available data.
    """
    pass
