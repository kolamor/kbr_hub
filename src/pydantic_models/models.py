from datetime import datetime

from pydantic import BaseModel, EmailStr
from uuid import UUID

# from wtforms.validators import Email


class BaseMedia(BaseModel):
    name: str
    url: str
    data: bytes | None


class BaseDatesMxn:
    created_at: datetime
    updated_at: datetime | None


class Permission(BaseModel):
    id: int
    name: str
    codename: str


class Group(BaseModel):
    id: int
    name: str
    description: str
    permission: Permission


class User(BaseModel):
    id: int
    uuid: UUID
    username: str
    first_name: str | None
    last_name: str | None
    email: EmailStr
    password: str
    groups: list[Group]
    user_permissions: list[Permission]
    is_staff: bool
    is_active: bool
    is_superuser: bool
    last_login: datetime
    date_joined: datetime


class Image(BaseMedia):
    pass


class Video(BaseMedia):
    pass


class DocumentMedia(BaseMedia):
    pass


class FileMedia(BaseMedia):
    pass

class Avatar(Image):
    pass


class Attachment(BaseModel):
    media: list[Image, Video, FileMedia, DocumentMedia]

class Tag(BaseModel):
    pass


class BaseItem(BaseModel):
    id: int
    name: str
    uuid: UUID
    parent_id: int | None
    description: str | None


class Brand(BaseItem):
    logo: Avatar
    images: list[Image] | None
    tags: list[Tag] | None


class Category(BaseItem):
    avatar: Avatar | None
    tags: list[Tag] | None


class Topic(BaseDatesMxn, BaseModel):
    avatar: Avatar
    user: User
    tags: list[Tag] | None


class Post(BaseDatesMxn, BaseModel):
    user: User
    attachments: list[Attachment]

