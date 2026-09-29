from collections.abc import AsyncIterator
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from nua.root_container import RootContainer


@inject
async def get_session(
    session_maker: Annotated[async_sessionmaker[AsyncSession], Depends(Provide[RootContainer.session_maker])]
) -> AsyncIterator[AsyncSession]:
    async with session_maker() as session:
        yield session
