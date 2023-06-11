import datetime
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_staff: Optional[bool]
    last_login: Optional[datetime.datetime]
    date_joined: datetime.datetime


class UserCreate(schemas.BaseUserCreate):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    date_joined: datetime.datetime = datetime.datetime.utcnow()


class UserUpdate(schemas.BaseUserUpdate):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]

    is_staff: Optional[bool]
    last_login: Optional[datetime.datetime]
    date_joined: datetime.datetime
