class ObjectNotFoundException(Exception):
    """
    Exception raised when an object is not found.
    """

    pass


class InvalidTokenException(Exception):
    """
    Exception raised for invalid tokens.
    """

    pass


class InvalidCredentialsException(Exception):
    """
    Exception raised for invalid authentication credentials.
    """

    pass
