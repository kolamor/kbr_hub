from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


class PsqlExt:
    def __init__(self, engine: AsyncEngine,
                 session_maker: async_sessionmaker):
        self.engine = engine
        self.session_marker = session_maker
