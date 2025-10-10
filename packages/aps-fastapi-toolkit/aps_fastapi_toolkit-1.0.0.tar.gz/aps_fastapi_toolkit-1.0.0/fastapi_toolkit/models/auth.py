from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

from fastapi_toolkit.utils import current_time_utc


class OutstandingToken(Base):
    """
    Model for storing outstanding JWT tokens.
    """

    __abstract__ = True
    __tablename__ = "outstanding_tokens"

    id = None  # type: ignore[assignment]
    jti: Mapped[str] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    def __str__(self) -> str:
        return self.jti


class BlacklistedToken(Base):
    """
    Model for storing blacklisted JWT tokens.
    """

    __abstract__ = True
    __tablename__ = "blacklisted_tokens"

    token_jti: Mapped[str] = mapped_column(
        ForeignKey("outstanding_tokens.jti", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    blacklisted_at: Mapped[datetime] = mapped_column(
        nullable=False, default=current_time_utc
    )

    def __str__(self) -> str:
        return self.token_jti
