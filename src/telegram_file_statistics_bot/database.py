"""
This module provides database functionalities for
the Telegram Bot for File Statistics. It includes classes and
functions to interact with the SQLite database.
"""

import json
import sqlite3
from typing import Dict

from . import get_str


class Database:
    """
    A singleton class to interact with the SQLite database for the
    Telegram Bot for File Statistics.

    Attributes:
    ----------
    db_path : str
        The file path to the database.
    """

    _instance = None
    db_path = ""

    def __init__(self, db_path: str | None = None):
        self._conn = None
        self._user_ids = []
        self._iter_index = 0
        if db_path:
            self.db_path = db_path

    def __new__(cls, db_path: str | None = None):
        """
        Ensures that only one instance of the Database class
        is created (Singleton pattern).

        Args:
            db_path (str): The file path to the SQLite database.

        Returns:
            Database: The singleton instance of the Database class.
        """
        if not cls._instance and not db_path:
            raise ValueError(get_str("Database path not set."))

        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # __init__ will be called after __new__
        return cls._instance

    def _connect(self):
        """
        Establishes a connection to the SQLite database.

        Returns:
            sqlite3.Connection: SQLite database connection object.
        """
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        """
        Initializes the database by creating the `user_data` table
        if it does not already exist. Adds ignored_extensions if missing.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER PRIMARY KEY,
                    total_size INTEGER DEFAULT 0,
                    total_download_size INTEGER DEFAULT 0,
                    file_count INTEGER DEFAULT 0,
                    streamable INTEGER DEFAULT 0,
                    extension_categories TEXT DEFAULT '{}',
                    ignored_extensions TEXT DEFAULT '[]'
                )"""
            )
            # Add ignored_extensions column if it doesn't exist (for upgrades)
            cursor.execute("PRAGMA table_info(user_data)")
            columns = [row[1] for row in cursor.fetchall()]
            if "ignored_extensions" not in columns:
                cursor.execute(
                    "ALTER TABLE user_data ADD COLUMN ignored_extensions TEXT DEFAULT '[]'"
                )
            conn.commit()

    def get_user_data(self, user_id: int) -> Dict:
        """
        Retrieves user data from the database based on the given user ID.

        Args:
            user_id (int): The ID of the user whose data is to be retrieved.

        Returns:
            Dict[str, int | Dict[str, int]]: A dictionary containing
            the user's data with default values if no data is found.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_data WHERE user_id=?", (user_id,))
            row = cursor.fetchone()

        if not row:
            return {
                "total_size": 0,
                "total_download_size": 0,
                "file_count": 0,
                "streamable": 0,
                "extension_categories": json.loads("{}"),
                "ignored_extensions": [],
            }
        # row: user_id, total_size, total_download_size, file_count, streamable, extension_categories, ignored_extensions
        return {
            "total_size": row[1],
            "total_download_size": row[2],
            "file_count": row[3],
            "streamable": row[4],
            "extension_categories": json.loads(row[5]),
            "ignored_extensions": json.loads(row[6]) if len(row) > 6 and row[6] else [],
        }

    def reset_user_data(self, user_id: int) -> None:
        """
        Resets the user data in the database.

        Args:
            - user_id (int): The ID of the user.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO user_data
                   (user_id, total_size, total_download_size,
                   file_count, streamable, extension_categories, ignored_extensions)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    0,
                    0,
                    0,
                    0,
                    json.dumps({}),
                    json.dumps([]),
                ),
            )
            conn.commit()

    def remove_extensions_from_user(self, user_id: int, extensions: list[str]) -> None:
        """
        Remove specified extensions from a user's extension_categories and update stats accordingly.

        Args:
            user_id (int): The ID of the user.
            extensions (list[str]): List of extensions to remove (e.g., ['.exe', '.mp3']).
        """
        user_data = self.get_user_data(user_id)
        ext_cats = user_data.get("extension_categories", {})
        removed = False
        for ext in extensions:
            if ext in ext_cats:
                ext_info = ext_cats.pop(ext)
                count = int(ext_info.get("count", 0))
                size = int(ext_info.get("size", 0))
                user_data["file_count"] = max(
                    0,
                    user_data["file_count"] - count,
                )
                user_data["total_size"] = max(0, user_data["total_size"] - size)
                user_data["total_download_size"] = max(
                    0,
                    user_data["total_download_size"] - size,
                )
                removed = True
        if removed:
            self.update_user_data(user_id, user_data)

    def update_user_data(self, user_id: int, data: Dict) -> None:
        """
        Updates the user data in the database.

        Args:
            - user_id (int): The ID of the user.
            - data (Dict[str, int | Dict[str, int]]): A dictionary containing
            the user data to be updated.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO user_data
                   (user_id, total_size, total_download_size,
                   file_count, streamable, extension_categories, ignored_extensions)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    data["total_size"],
                    data["total_download_size"],
                    data["file_count"],
                    data["streamable"],
                    json.dumps(data["extension_categories"]),
                    json.dumps(data.get("ignored_extensions", [])),
                ),
            )
            conn.commit()

    def is_stats_empty(self, user_id: int) -> bool:
        """
        Checks if the user's statistics are empty.

        Args:
            user_id (int): The ID of the user.

        Returns:
            bool: True if the user's statistics are empty, False otherwise.
        """
        user_data = self.get_user_data(user_id)
        return all(
            [
                user_data["total_size"] == 0,
                user_data["total_download_size"] == 0,
                user_data["file_count"] == 0,
                user_data["streamable"] == 0,
                not user_data["extension_categories"],
            ]
        )

    def __str__(self):
        return f"<Database db_path='{self.db_path}'>"

    def __repr__(self):
        return f"Database(db_path={self.db_path!r})"

    def __len__(self):
        # Number of users in the database
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_data")
            return cursor.fetchone()[0]

    def __getitem__(self, user_id):
        # Always return a dict, like get_user_data
        return self.get_user_data(user_id)

    def __setitem__(self, user_id, value):
        self.update_user_data(user_id, value)

    def __contains__(self, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM user_data WHERE user_id=?", (user_id,))
            return cursor.fetchone() is not None

    def __delitem__(self, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_data WHERE user_id=?", (user_id,))
            conn.commit()

    def __enter__(self):
        self._conn = self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __iter__(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_data")
            self._user_ids = [row[0] for row in cursor.fetchall()]
        self._iter_index = 0
        return self

    def __next__(self):
        if not self._user_ids:
            self.__iter__()
        if self._iter_index >= len(self._user_ids):
            self._user_ids = []
            raise StopIteration
        user_id = self._user_ids[self._iter_index]
        self._iter_index += 1
        return user_id

    def __missing__(self, user_id):
        # Only called if used as a dict subclass, but provided for completeness
        return self.get_user_data(user_id)
