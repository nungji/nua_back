import asyncio
import logging

import reger
import uvicorn
from fastapi import FastAPI

from nua import api
from nua.app import create_app
from nua.config import Config
from nua.root_container import RootContainer

_logger = logging.getLogger(__name__)


class Bootstrapper:
    def __init__(self, root_container: RootContainer):
        self.root_container: RootContainer = root_container
        self.config: Config = self.root_container.config()
        self.app: FastAPI = create_app(
            engine=self.root_container.engine(),
            cors_origins=self.config.cors_origins
        )

    def run(self):
        asyncio.run(self.arun())

    async def arun(self):
        print('Bootstrapper: Setup logging...')
        self.setup_logging()
        _logger.info('If you can see it, logging setup is complete')

        self.root_container.wire(modules=[api.dependencies])

        _logger.info('Starting uvicorn...')
        server = uvicorn.Server(
            uvicorn.Config(
                self.app,
                host=self.config.host,
                port=self.config.port,
                log_config=None
            )
        )
        _logger.info('Bootstrapping is complete! now you just waiting for actual log with delicious ramyeon')

        await server.serve()

    def setup_logging(self):
        root_logger = logging.getLogger()

        reger.setup_logging(level=logging.INFO)

        if self.config.log_file_path:
            file_handler = logging.FileHandler(filename=self.config.log_file_path, encoding='utf-8')
            file_handler.setFormatter(reger.ColourFormatter())
            root_logger.addHandler(file_handler)
