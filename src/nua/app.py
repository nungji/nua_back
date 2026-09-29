import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from nua.api.errors import register_exception_handlers
from nua.api.routes import api_router

_logger = logging.getLogger(__name__)


def create_app(engine: AsyncEngine, cors_origins: list[str]) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        _logger.info('nua backend has started')
        yield
        _logger.info('nua backend is shutting down')
        await engine.dispose()

    app = FastAPI(title='nua backend', lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=['*'],
        allow_headers=['*']
    )

    app.include_router(api_router)
    register_exception_handlers(app)

    return app
