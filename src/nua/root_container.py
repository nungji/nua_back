from dependency_injector import containers
from dependency_injector.providers import Singleton
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from nua import config
from nua.db.session import create_engine, create_session_maker


class RootContainer(containers.DeclarativeContainer):
    config: Singleton[config.Config] = \
        Singleton(config.get_config_from_env)

    engine: Singleton[AsyncEngine] = \
        Singleton(create_engine, database_url=config.provided.database_url)

    session_maker: Singleton[async_sessionmaker[AsyncSession]] = \
        Singleton(create_session_maker, engine=engine)
