from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import DeclarativeBase

from src.alchemy_models.db import user_table, meta


class Base(DeclarativeBase):
    metadata = meta


class User(SQLAlchemyBaseUserTable, Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = user_table.name
    # id: Mapped[int] = mapped_column(Integer, primary_key=True)
