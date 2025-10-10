from fastapi import Depends
from typing import Annotated


from .db import DBDependency
from fastapi_toolkit.services import UserService


def _get_user_service(db: DBDependency) -> UserService:
    """
    Dependency to get an instance of UserService.
    """
    return UserService(db)


UserServiceDependency = Annotated[UserService, Depends(_get_user_service)]
