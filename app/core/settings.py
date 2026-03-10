from functools import lru_cache
from os import cpu_count

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    max_concurrent_exports: int = 8
    process_pool_workers: int = max(1, min(cpu_count() or 1, 4))
    upload_chunk_size: int = 1024 * 1024
    semaphore_acquire_timeout_seconds: float = 3.0
    max_total_lines: int = 10_000
    max_unique_lemmas: int = 200_000
    excel_max_cell_chars: int = 32_767


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
