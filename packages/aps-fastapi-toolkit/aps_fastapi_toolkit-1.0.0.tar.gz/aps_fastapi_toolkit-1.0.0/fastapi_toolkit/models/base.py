from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from fastapi_toolkit.utils import current_time_utc


class Base(DeclarativeBase):
    """
    Base class for all models.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=current_time_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, default=None, onupdate=current_time_utc
    )
