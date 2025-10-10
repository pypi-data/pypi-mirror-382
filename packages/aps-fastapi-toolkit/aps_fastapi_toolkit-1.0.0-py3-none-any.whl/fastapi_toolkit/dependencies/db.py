from typing import Annotated, Generator, Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from fastapi_toolkit.services import DatabaseService

# Will be set once by the consuming app
_db_service: Optional[DatabaseService] = None


def init_db_dependency(service: DatabaseService) -> None:
    """
    Initialize the global DatabaseService for dependency injection.
    This should be called once during app startup.
    """
    global _db_service
    _db_service = service


def _get_db() -> Generator[Session, None, None]:
    """
    Actual FastAPI dependency function that yields a DB session.
    """
    if _db_service is None:
        raise RuntimeError(
            "DatabaseService is not initialized. "
            "Call `init_db_dependency()` during startup."
        )

    yield from _db_service.get_db_session()


# The annotated FastAPI dependency you can import everywhere
DBDependency = Annotated[Session, Depends(_get_db)]
