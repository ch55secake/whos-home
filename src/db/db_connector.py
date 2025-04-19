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
            self.connection.row_factory = sqlite3.Row
            Logger().debug("Database connection established")
        except sqlite3.Error as e:
            Logger().debug(f"Database connection failed {e}")
            raise e

        if run_migration:
            self.__initialize_db()

    def find_one(self, query: str, params: Any = None) -> Any:
        return self.__execute_query(query, params)

    def find_all(self, query: str, params: Any = None) -> Any:
        return self.__execute_query(query, params, fetch_one=False)

    def __execute_query(self, query: str, params: Any = None, fetch_one: bool = True) -> Any:
        with closing(self.connection.cursor()) as cursor:
            try:
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                if fetch_one:
                    return cursor.fetchone()
                return cursor.fetchall()
            except sqlite3.Error as e:
                Logger().debug(f"Query failed with error: {e}")
                raise e

    def __initialize_db(self) -> None:
        Logger().debug("Migrating database...")
        with open(SCHEMA_SQL, "r", encoding="utf-8") as file:
            sql: str = file.read()

        for query in sql.split(";"):
            self.__execute_query(query)

    def close(self):
        if self.connection:
            self.connection.close()
            Logger().debug("Database connection closed")
            self.connection = None
