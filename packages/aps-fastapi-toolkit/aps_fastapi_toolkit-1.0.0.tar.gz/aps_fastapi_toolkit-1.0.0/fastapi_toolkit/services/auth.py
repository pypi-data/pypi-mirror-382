import jwt
import uuid
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from typing import Dict, Any, Literal

from fastapi_toolkit.utils import TokenTypes
from fastapi_toolkit.schemas import (
    LoginTokens,
    JWTTokenPayload,
    AccessToken,
    RefreshToken,
)
from fastapi_toolkit.utils import CookieNames


class JWTService:
    """
    Service class for handling JSON Web Tokens (JWT).
    """

    def __init__(
        self,
        secret_key: str,
        access_token_lifetime: timedelta,
        refresh_token_lifetime: timedelta,
        algorithm: str | None = None,
    ):
        """
        Initialize the JWTService with a secret key and algorithm.
        """
        self._secret_key = secret_key
        self._algorithm = algorithm or "HS256"
        self._access_token_lifetime = access_token_lifetime
        self._refresh_token_lifetime = refresh_token_lifetime

    def __token_expiration_time(
        self, is_refresh: bool, lifetime: timedelta | None
    ) -> timedelta:
        """
        Returns the expiration time for the token.
        """
        if lifetime:
            return lifetime

        if is_refresh:
            return self._refresh_token_lifetime
        return self._access_token_lifetime

    def __create_token(
        self,
        data: Dict[str, Any],
        type: TokenTypes,
        lifetime: timedelta | None = None,
    ) -> RefreshToken | AccessToken:
        """
        Creates a JWT token for user.
        """
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())
        is_refresh = type == TokenTypes.REFRESH

        payload = JWTTokenPayload(
            data=data,
            iat=now,
            exp=now + self.__token_expiration_time(is_refresh, lifetime),
            jti=jti,
            type=type.value,
            refresh=is_refresh,
        )
        token = jwt.encode(  # type: ignore
            payload=payload.model_dump(),
            key=self._secret_key,
            algorithm=self._algorithm,
        )
        return (
            RefreshToken(token=token, jti=jti)
            if is_refresh
            else AccessToken(token=token)
        )

    def get_access_token(
        self, data: Dict[str, Any], lifetime: timedelta | None = None
    ) -> AccessToken:
        """
        Creates an access JWT token for user.
        """
        return self.__create_token(data, TokenTypes.ACCESS, lifetime=lifetime)

    def get_refresh_token(
        self, data: Dict[str, Any], lifetime: timedelta | None = None
    ) -> RefreshToken:
        """
        Creates a refresh JWT token for user.
        """
        return self.__create_token(data, TokenTypes.REFRESH, lifetime=lifetime)  # type: ignore

    def decode_token(self, token: str) -> JWTTokenPayload:
        """
        Decodes the JWT token and return the payload.
        """
        payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])  # type: ignore
        return JWTTokenPayload.model_validate(payload)

    @property
    def access_token_lifetime(self) -> timedelta:
        """
        Returns the access token lifetime.
        """
        return self._access_token_lifetime

    @property
    def refresh_token_lifetime(self) -> timedelta:
        """
        Returns the refresh token lifetime.
        """
        return self._refresh_token_lifetime


class CookieService:
    """
    Service for handling cookie-related operations.
    """

    def __init__(
        self, access_token_lifetime: timedelta, refresh_token_lifetime: timedelta
    ) -> None:
        self._access_token_lifetime = access_token_lifetime
        self._refresh_token_lifetime = refresh_token_lifetime

    def create_cookie(
        self,
        response: JSONResponse,
        token: str,
        lifetime: timedelta,
        refresh: bool = False,
        csrf: bool = False,
        secure: bool = True,
        samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        """
        Creates a cookie for the token.
        """
        key = CookieNames.ACCESS.value

        if refresh or csrf:
            key = CookieNames.REFRESH.value if refresh else CookieNames.CSRF.value

        response.set_cookie(
            key=key,
            value=token,
            httponly=not csrf,
            secure=secure,
            samesite=samesite,
            max_age=int(lifetime.total_seconds()),
        )

    def create_login_cookies_response(
        self, data: LoginTokens, message: str = "Login successful."
    ) -> JSONResponse:
        """
        Create cookies for login.
        """
        response = JSONResponse({"detail": message})
        self.create_cookie(response, data.access_token, self._access_token_lifetime)
        self.create_cookie(
            response,
            data.refresh_token,
            refresh=True,
            lifetime=self._refresh_token_lifetime,
        )
        self.create_cookie(
            response, data.csrf_token, csrf=True, lifetime=self._refresh_token_lifetime
        )
        return response

    def remove_all_cookies(self, message: str = "Logout successful.") -> JSONResponse:
        """
        Remove all authentication cookies to logout.
        """
        response = JSONResponse({"detail": message})
        response.delete_cookie(CookieNames.ACCESS.value)
        response.delete_cookie(CookieNames.REFRESH.value)
        response.delete_cookie(CookieNames.CSRF.value)
        return response
