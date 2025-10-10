from enum import Enum


class CookieNames(Enum):
    """
    Enumeration for cookie names.
    """

    ACCESS = "access_token"
    REFRESH = "refresh_token"
    CSRF = "csrf_token"


class TokenTypes(Enum):
    """
    Enumeration for token types.
    """

    ACCESS = "access"
    REFRESH = "refresh"
