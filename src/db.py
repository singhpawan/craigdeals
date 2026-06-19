import logging
import os

from sqlalchemy import create_engine, inspect, text

logger = logging.getLogger(__name__)


def get_engine():
    url = os.environ["DATABASE_URL"]
    # SQLAlchemy 2.x requires postgresql:// scheme
    url = url.replace("postgres://", "postgresql://", 1)
    return create_engine(url)


def table_exists(engine, table_name: str) -> bool:
    return inspect(engine).has_table(table_name)


def drop_if_exists(engine, table_name: str) -> None:
    if table_exists(engine, table_name):
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE {table_name}"))
            conn.commit()
        logger.info("Dropped table %s", table_name)
