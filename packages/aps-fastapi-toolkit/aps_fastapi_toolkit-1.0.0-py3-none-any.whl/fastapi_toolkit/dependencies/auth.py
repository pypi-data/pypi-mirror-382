from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from typing import Any

from .user import UserServiceDependency
from fastapi_toolkit.utils import CookieNames
from fastapi_toolkit.services import JWTService, CookieService

# -------------------- OAuth2 Scheme Dependency -------------------- #

_token_url = None


def set_token_url(url: str):
    """
    Set the token URL for OAuth2PasswordBearer.
    """
    global _token_url
    _token_url = url


async def _get_oauth2_scheme() -> OAuth2PasswordBearer:
    if not _token_url:
        raise RuntimeError("Token URL is not set. Call `set_token_url()` first.")
    return OAuth2PasswordBearer(tokenUrl=_token_url, auto_error=False)


# -------------------- JWT Service Dependency -------------------- #
_jwt_service = None


def init_jwt_service(service: JWTService):
    """
    Initialize the JWT service.
    """
    global _jwt_service
    _jwt_service = service


async def _get_jwt_service() -> JWTService:
    """
    Returns the JWT service instance.
    """
    if _jwt_service is None:
        raise RuntimeError(
            "JWT service is not initialized. "
            "Call `init_jwt_service()` during startup."
        )
    return _jwt_service


JWTServiceDependency = Annotated[JWTService, Depends(_get_jwt_service)]


# -------------------- Cookie Service Dependency -------------------- #


async def _get_cookie_service(jwt_service: JWTServiceDependency) -> CookieService:
    """
    Returns the Cookie service instance.
    """
    return CookieService(
        jwt_service.access_token_lifetime, jwt_service.refresh_token_lifetime
    )


CookieServiceDependency = Annotated[CookieService, Depends(_get_cookie_service)]


# -------------------- Auth Dependency -------------------- #


async def _get_user(
    token: str | None,
    jwt_service: JWTServiceDependency,
    user_service: UserServiceDependency,
):
    """
    Returns the currently authenticated user based on the token.
    """
    if token is None:
        return None

    payload = jwt_service.decode_token(token)

    if payload.type != "access":
        return None

    email = payload.data.get("email")

    if email is None:
        return None

    return user_service.get_user_by_email(email)


async def _get_current_authenticated_user_cookie(
    request: Request,
    jwt_service: JWTServiceDependency,
    user_service: UserServiceDependency,
):
    return _get_user(
        request.cookies.get(CookieNames.ACCESS.value),
        jwt_service,
        user_service,
    )


async def _get_current_authenticated_user(
    jwt_service: JWTServiceDependency,
    user_service: UserServiceDependency,
    token: Annotated[str | None, Depends(_get_oauth2_scheme)] = None,
):
    return _get_user(
        token,
        jwt_service,
        user_service,
    )


async def _is_user_authenticated(user: Any):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to continue.",
        )
    return user


async def _is_anonymous(user: Any):
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already logged in.",
        )
    return None


async def is_authenticated_cookie(
    user: Annotated[Any, Depends(_get_current_authenticated_user_cookie)],
):
    """
    Dependency to check if the user is authenticated (using cookies).
    """
    return _is_user_authenticated(user)


async def is_anonymous_cookie(
    user: Annotated[Any, Depends(_get_current_authenticated_user_cookie)],
):
    """
    Dependency to check if the user is anonymous (using cookies).
    """
    return _is_anonymous(user)


async def is_authenticated_header(
    user: Annotated[Any, Depends(_get_current_authenticated_user)],
):
    """
    Dependency to check if the user is authenticated (using Headers).
    """
    return _is_user_authenticated(user)


async def is_anonymous_header(
    user: Annotated[Any, Depends(_get_current_authenticated_user)],
):
    """
    Dependency to check if the user is anonymous (using headers).
    """
    return _is_anonymous(user)
