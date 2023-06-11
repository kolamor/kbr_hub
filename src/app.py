import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from src.core.psql import PsqlExt
from src.routes.base_routes import create_routes
from src.settings import Config
from src.utils.extend import Singleton


logger = logging.getLogger(__name__)


def get_app_ext() -> 'AppExt':
    return get_app_ext.__app_ext


def set_app_ext(app_ext: 'AppExt') -> None:
    get_app_ext.__app_ext = app_ext


class AppExt(metaclass=Singleton):

    def __init__(self, *, app: FastAPI, config: Config,
                 sql_alchemy_engine: Optional[str] = None,
                 psql_ext: Optional[PsqlExt] = None):
        self.app: FastAPI = app
        self.config: Config = config
        self.sql_alchemy_engine: AsyncEngine | None = sql_alchemy_engine
        self.psql_ext = psql_ext

    @classmethod
    def get_instance(cls):
        return

def create_app(config: Config):

    app = FastAPI(lifespan=lifespan)
    set_app_ext(AppExt(app=app, config=config))
    create_routes(app=app)
    # from .users.auth import routes
    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_ext = get_app_ext()
    await on_startup(app, app_ext)
    from .users.auth import routes
    from .admin import admin_map
    yield
    await on_shutdown(app,  app_ext)


async def on_startup(app: FastAPI, app_ext: AppExt):
    config: Config = app_ext.config

    db_connect_kwargs = config.POSTGRESQL_DSN_OPTIONS if config.POSTGRESQL_DSN_OPTIONS else {}

    # postgresql
    cred = config.POSTGRESQL_DSN.split('://')[-1]
    engine = create_async_engine(
        f"postgresql+asyncpg://{cred}", echo=config.POSTGRESQL_ENGINE_PRE, **db_connect_kwargs
    )
    app_ext.sql_alchemy_engine = engine
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    psql_ext = PsqlExt(engine=engine, session_maker=async_session)
    app_ext.psql_ext = psql_ext

    from .users import users_f



async def on_shutdown(app: FastAPI, app_ext: AppExt):
    engine = app_ext.sql_alchemy_engine
    await engine.dispose()
    logger.info('PSQL closed')
    print('PSQL closed')

