import re
from functools import lru_cache
from typing import Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError


class ArgonHashUtility:
    """
    ArgonHashUtility provides methods to hash and
    verify passwords using the PasswordHasher.
    """

    def __init__(self):
        self._ph = PasswordHasher()

    def hash_value(self, value: str) -> str:
        """
        Hash the value using the Argon2 PasswordHasher.
        """
        return self._ph.hash(value)

    def verify_value(self, hashed_value: str, value: str) -> Tuple[bool, bool]:
        """
        Verifies if the provided value matches the hashed value.

        Returns:
            Tuple(bool, bool):
            - A boolean indicating whether the value is correct.
            - A boolean indicating whether the hash needs to be updated (rehash).
        """

        try:
            verified = self._ph.verify(hashed_value, value)
            return verified, self._ph.check_needs_rehash(hashed_value)

        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False, False


@lru_cache
def get_argon_hasher() -> ArgonHashUtility:
    """
    Returns a cached instance of ArgonHashUtility.
    """
    return ArgonHashUtility()


def validate_strong_password(password: str) -> str:
    """
    Validates the given password based on the following criteria:
    - Must contain at least 1 lowercase letter.
    - Must contain at least 1 uppercase letter.
    - Must contain at least 1 digit.
    - Must contain at least 1 special character from (@, #, $).
    - Must be at least 8 characters long.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least 1 lowercase letter")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least 1 uppercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least 1 digit")
    if not re.search(r"[@#$]", password):
        raise ValueError(
            "Password must contain at least 1 special character from (@, #, $)"
        )
    return password
