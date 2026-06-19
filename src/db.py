import logging
import os
from typing import Optional

from sqlalchemy import create_engine, Engine, inspect, text

logger = logging.getLogger(__name__)

_ALLOWED_TABLES = {"scraped", "priced"}

_engine: Optional[Engine] = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def table_exists(engine: Engine, table_name: str) -> bool:
    return inspect(engine).has_table(table_name)


def drop_if_exists(engine: Engine, table_name: str) -> None:
    if table_name not in _ALLOWED_TABLES:
        raise ValueError(f"Refusing to drop unknown table '{table_name}'")
    if table_exists(engine, table_name):
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE {table_name}"))
            conn.commit()
        logger.info("Dropped table %s", table_name)
