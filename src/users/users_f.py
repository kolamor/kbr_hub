from typing import Optional, AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin,  FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import AuthenticationBackend, \
    JWTStrategy, CookieTransport
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from . import app_ext
from .db import User

SECRET = app_ext.config.AUTH_SECRET_KEY

cookie_transport = CookieTransport(cookie_max_age=3600, cookie_name='sess',
                                   cookie_httponly=False)
# bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="cookie",
    # transport=bearer_transport,
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    # user_db = user_table

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async_session_maker = app_ext.psql_ext.session_marker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users_local = FastAPIUsers[User, id](get_user_manager, [auth_backend])

