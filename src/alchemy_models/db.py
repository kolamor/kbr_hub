from sqlalchemy import (
    Table, Text, Integer, VARCHAR, MetaData, Column, BOOLEAN, ForeignKey, DateTime,
    UniqueConstraint, Float, Enum, ForeignKeyConstraint, PrimaryKeyConstraint, UUID, func,
)

__all__ = ('user_table', )

from sqlalchemy.dialects.postgresql import JSONB, BIGINT, ENUM

meta = MetaData()

group_table = Table(
    'group', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', VARCHAR(150), unique=True),
    Column('description', Text, unique=True),
)


permission_table = Table(
    'permission', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', VARCHAR(255), unique=True),
    Column('codename', VARCHAR(255), unique=True)
)

user_group_table = Table(
    'user_group', meta,
    Column('user_id', ForeignKey('app_user.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', ForeignKey('group.id', ondelete='CASCADE'), primary_key=True),
    PrimaryKeyConstraint('user_id', 'group_id')
)

user_permission_table = Table(
    'user_permission', meta,
    Column('user_id', ForeignKey('app_user.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', ForeignKey('permission.id', ondelete='CASCADE'), primary_key=True),
    PrimaryKeyConstraint('user_id', 'permission_id')
)

group_permission_table = Table(
    'group_permission', meta,
    Column('group_id', ForeignKey('group.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', ForeignKey('permission.id', ondelete='CASCADE'), primary_key=True),
    PrimaryKeyConstraint('group_id', 'permission_id')
)


user_table = Table(
    'app_user', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    # Column('uuid', UUID, unique=True),
    Column('username', VARCHAR(150), unique=True),
    Column('first_name', VARCHAR(150), nullable=True),
    Column('last_name', VARCHAR(150), nullable=True),
    Column('email', VARCHAR(320), index=True, nullable=False),
    # Column('password', VARCHAR, nullable=False),
    Column('hashed_password', VARCHAR(1024), nullable=False),
    Column('is_verified', BOOLEAN, nullable=False, default=False),
    Column('is_staff', BOOLEAN, nullable=False, default=False),
    Column('is_active', BOOLEAN, nullable=False, default=True),
    Column('is_superuser', BOOLEAN, nullable=False, default=False),
    Column('last_login', DateTime(timezone=False), nullable=True),
    Column('date_joined', DateTime(timezone=False), server_default=func.utcnow()),
)


item_type_table = Table(
    'item_type', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', VARCHAR(150), unique=True),
    Column('description', Text, nullable=True),
)


item_brand_table = Table(
    'item_brand', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', VARCHAR(150), unique=True),
    Column('description', Text, nullable=True)
)


item_table = Table(
    'item_table', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', VARCHAR(255), unique=True),
    Column('photo_url', VARCHAR(255), nullable=True),
    Column('description', Text, nullable=True),
    Column('item_type_id', ForeignKey('item_type.id', ondelete='CASCADE')),
    Column('item_brand_id', ForeignKey('item_brand.id', ondelete='CASCADE')),
    Column('other_info', JSONB, nullable=True),
)
