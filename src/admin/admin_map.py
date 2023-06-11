from sqladmin import Admin, ModelView
from sqlalchemy.orm import DeclarativeBase

from src.alchemy_models.db import user_table, meta
from src.alchemy_models import db

from src.users import app_ext


admin = Admin(app_ext.app, app_ext.sql_alchemy_engine)


class Base(DeclarativeBase):
    metadata = meta


class AppUser(Base):
    __tablename__ = 'app_user'


class UserAdmin(ModelView, model=AppUser):
    column_list = [str(c.name) for c in user_table.columns if c.name not in {'hashed_password'}]


class UserGroup(Base):
    __tablename__ = db.group_table.name


class UserGroupAdmin(ModelView, model=UserGroup):
    column_list = [c.name for c in db.group_table.columns]


class UserPermission(Base):
    __tablename__ = db.permission_table.name


class UserPermissionAdmin(ModelView, model=UserPermission):
    column_list = [c.name for c in db.permission_table.columns]


# class GroupPermission(Base):
#     __tablename__ = db.group_permission_table.name
#
#
# class GroupPermissionAdmin(ModelView, model=GroupPermission):
#     column_list = [c.name for c in db.group_permission_table.columns]

models = [UserAdmin, UserGroupAdmin, UserPermissionAdmin, ]
[admin.add_view(model) for model in models]
