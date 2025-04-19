import os
import sqlite3
from contextlib import closing
from sqlite3 import Connection
from typing import Any

from src.util.logger import Logger

# TODO- env var or something else
DB_PATH = "database.db"
SCHEMA_SQL = "resources/schema.sql"


class DatabaseConnector:
    def __init__(self) -> None:
        self.connection: Connection | None = None

    def connect(self) -> None:
        run_migration: bool = not os.path.exists(DB_PATH)

        try:
            self.connection = sqlite3.connect(DB_PATH)
            Logger().debug("Database connection established")
        except sqlite3.Error as e:
            Logger().debug(f"Database connection failed {e}")
            raise e

        if run_migration:
            self.__migrate()

    def execute_query(self, query: str, params: Any = None) -> Any:
        if self.connection is None:
            self.connect()
        with closing(self.connection.cursor()) as cursor:
            try:
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                return cursor.fetchall()
            except sqlite3.Error as e:
                Logger().debug(f"Query failed with error: {e}")
                raise e

    def __migrate(self) -> None:
        Logger().debug("Migrating database...")
        with open(SCHEMA_SQL, "r", encoding="utf-8") as file:
            sql: str = file.read()

        for query in sql.split(";"):
            self.connection.execute(query)

    def close(self):
        if self.connection:
            self.connection.close()
            Logger().debug("Database connection closed")
            self.connection = None
