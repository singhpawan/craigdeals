from __future__ import annotations

import logging
from functools import lru_cache

from sqlalchemy import Engine, create_engine, inspect, text

from .config import get_settings

logger = logging.getLogger(__name__)

_MANAGED_TABLES = {"scraped", "priced"}


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    url = get_settings().database_url.replace("postgres://", "postgresql://", 1)
    return create_engine(url, pool_pre_ping=True)


def table_exists(engine: Engine, table_name: str) -> bool:
    return inspect(engine).has_table(table_name)


def clear_table(engine: Engine, table_name: str) -> None:
    if table_name not in _MANAGED_TABLES:
        raise ValueError(f"Refusing to clear unknown table '{table_name}'")
    with engine.connect() as conn:
        conn.execute(text(f"DELETE FROM {table_name}"))
        conn.commit()
    logger.info("Cleared table %s", table_name)
