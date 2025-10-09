import sqlite3
from typing import TYPE_CHECKING

from . import models as m
from . import query as q
from . import sqla as sa
from . import types as t

if TYPE_CHECKING:
    from sqlalchemy.engine.interfaces import DBAPIConnection
    from sqlalchemy.pool import ConnectionPoolEntry

models = m
query = q
sqla = sa
types = t


@sqla.event.listens_for(sqla.Engine, "connect")
def set_sqlite_pragma(
    dbapi_connection: "DBAPIConnection", connection_record: "ConnectionPoolEntry"
) -> None:
    """Enable sqlite `foreign_keys` feature upon connecting."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
