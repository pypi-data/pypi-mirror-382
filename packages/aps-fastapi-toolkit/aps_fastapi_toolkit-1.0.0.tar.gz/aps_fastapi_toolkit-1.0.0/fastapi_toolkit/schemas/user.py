from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """
    Schema for creating a new user.
    """

    email: EmailStr
    password: str
    name: str


class SuperUser(User):
    """
    Schema for creating a new superuser.
    """

    is_superuser: bool = True
    is_staff: bool = True
    is_active: bool = True
