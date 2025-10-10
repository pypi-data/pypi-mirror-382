from getpass import getpass
from typing import Type
from sqlalchemy.orm import Session

from fastapi_toolkit.exceptions import ObjectNotFoundException
from fastapi_toolkit.models import User as DefaultUser
from fastapi_toolkit.schemas import User, SuperUser
from fastapi_toolkit.utils import get_argon_hasher

_argon_hasher = get_argon_hasher()


class UserService:
    """
    Service class for user-related operations.
    """

    _user_model: Type[DefaultUser] = DefaultUser

    @classmethod
    def set_user_model(cls, model: Type[DefaultUser]) -> None:
        """
        Set a custom user model class.

        Arguments:
            - `model` - The custom user model class to use.
        """
        cls._user_model = model

    @classmethod
    def get_user_model(cls) -> Type[DefaultUser]:
        """
        Returns the active User model (custom or default).
        """
        return cls._user_model

    def __init__(self, db: Session):
        self._db = db
        self._model = self.get_user_model()

    def create_user(self, user: User | SuperUser) -> None:
        """
        Create a new user in the database.
        """
        user.password = _argon_hasher.hash_value(user.password)
        new_user = self._model(**user.model_dump())
        self._db.add(new_user)
        self._db.commit()

    def get_user_by_email(self, email: str):
        """
        Retrieve a user by email.
        """
        user = self._db.query(self._model).filter_by(email=email).first()
        return user

    def get_user_by_id(self, id: int):
        """
        Retrieve a user  by ID.
        """
        user = self._db.query(self._model).filter_by(id=id).first()
        return user

    def user_exists(self, email: str) -> bool:
        """
        Check if a user exists in the database.
        """
        return self.get_user_by_email(email) is not None

    def create_superuser(self):
        """
        Create a superuser with predefined credentials.
        """
        name: str = input("Enter name: ")
        email: str = input("Enter email: ")
        password: str = getpass("Enter password: ")
        confirm_password: str = getpass("Confirm password: ")

        if password != confirm_password:
            raise ValueError("The two passwords do not match.")

        if self.user_exists(email):
            raise ValueError("User with this email already exists.")

        superuser = SuperUser(email=email, password=password, name=name)
        self.create_user(superuser)

    def delete_user(self, email: str) -> None:
        """
        Delete a user from the database.
        """
        user = self.get_user_by_email(email)

        if not user:
            raise ObjectNotFoundException("User not found.")

        self._db.delete(user)
        self._db.commit()
