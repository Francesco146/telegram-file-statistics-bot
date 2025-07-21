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
            cls._instance.db_path = db_path
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
        if it does not already exist.
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
                    extension_categories TEXT DEFAULT '{}'
                )"""
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
            }
        return {
            "total_size": row[1],
            "total_download_size": row[2],
            "file_count": row[3],
            "streamable": row[4],
            "extension_categories": json.loads(row[5]),
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
                   file_count, streamable, extension_categories)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    0,
                    0,
                    0,
                    0,
                    json.dumps({}),
                ),
            )
            conn.commit()

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
                   file_count, streamable, extension_categories)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    data["total_size"],
                    data["total_download_size"],
                    data["file_count"],
                    data["streamable"],
                    json.dumps(data["extension_categories"]),
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
