import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    database_url: str
    host: str
    port: int
    cors_origins: list[str]
    log_file_path: str | None


def get_config_from_env() -> Config:
    load_dotenv()

    return Config(
        os.getenv('DATABASE_URL'),
        os.getenv('HOST', '0.0.0.0'),
        int(os.getenv('PORT', '8000')),
        os.getenv('CORS_ORIGINS', '*').split(','),
        os.getenv('LOG_FILE')
    )
