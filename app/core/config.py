import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
	database_url: str = os.getenv("DATABASE_URL", "sqlite:///./job_processing.db")


@lru_cache
def get_settings() -> Settings:
	return Settings()
