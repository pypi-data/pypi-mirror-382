"""Exceptions raised by the api."""


class GllApiError(Exception):
    """General GllApi exception."""


class ConnectError(GllApiError):
    """Error connecting to Gallagher server."""


class UnauthorizedError(GllApiError):
    """Authentication failed."""


class LicenseError(GllApiError):
    """Missing license error."""


class RequestError(GllApiError):
    """Request error."""
