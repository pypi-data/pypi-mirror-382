from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, Literal


class LoginTokens(BaseModel):
    """
    Tokens returned upon successful login.
    """

    access_token: str
    refresh_token: str
    csrf_token: str


class JWTTokenPayload(BaseModel):
    """
    Payload contained in a JWT token.
    """

    data: Dict[str, Any]
    iat: datetime
    exp: datetime
    jti: str
    type: Literal["access", "refresh"]
    refresh: bool


class AccessToken(BaseModel):
    """
    Access token model.
    """

    token: str


class RefreshToken(AccessToken):
    """
    Refresh token model.
    """

    jti: str
