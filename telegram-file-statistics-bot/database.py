import json
import sqlite3


class Database:
    """
    A class used to represent the Database through a file path.

    Attributes
    ----------
    db_path : str
        The file path to the database.
    """

    db_path: str


def init_db() -> None:
    """
    Initializes the database by creating the 'user_data' table if it does not already exist.

    The 'user_data' table has the following columns:
    - user_id: INTEGER, primary key
    - total_size: INTEGER, default value is 0
    - total_download_size: INTEGER, default value is 0
    - file_count: INTEGER, default value is 0
    - streamable: INTEGER, default value is 0
    - extension_categories: TEXT, default value is '{}'

    This function connects to the database, executes the SQL command to create the table,
    commits the changes, and then closes the connection.
    """
    conn = sqlite3.connect(Database.db_path)
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
    conn.close()


def get_user_data(user_id: int) -> dict:
    """
    Retrieve user data from the database based on the given user ID.

    Args:
        user_id (int): The ID of the user whose data is to be retrieved.

    Returns:
        dict: A dictionary containing the user's data with the following keys:
            - "total_size" (int): The total size of the user's files.
            - "total_download_size" (int): The total size that the user needs to download.
            - "file_count" (int): The number of files the user has.
            - "streamable" (int): The number of streamable files the user has.
            - "extension_categories" (dict): A dictionary of file extension categories.

        If the user data is not found, returns a dictionary with default values:
            - "total_size": 0
            - "total_download_size": 0
            - "file_count": 0
            - "streamable": 0
            - "extension_categories": {}
    """
    conn = sqlite3.connect(Database.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {
            "total_size": 0,
            "total_download_size": 0,
            "file_count": 0,
            "streamable": 0,
            "extension_categories": {},
        }
    return {
        "total_size": row[1],
        "total_download_size": row[2],
        "file_count": row[3],
        "streamable": row[4],
        "extension_categories": json.loads(row[5]),
    }


def update_user_data(user_id: int, data: dict) -> None:
    """
    Updates the user data in the database.

    This function inserts or replaces a record in the `user_data` table with the provided
    user ID and data. The data dictionary should contain the following keys:
    - "total_size": The total size of the user's data.
    - "total_download_size": The total size that the user needs to download.
    - "file_count": The number of files associated with the user.
    - "streamable": A boolean indicating if the data is streamable.
    - "extension_categories": A dictionary of file extension categories.

    Args:
        user_id (int): The ID of the user.
        data (dict): A dictionary containing the user data to be updated.

    Returns:
        None
    """
    conn = sqlite3.connect(Database.db_path)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO user_data 
           (user_id, total_size, total_download_size, file_count, streamable, extension_categories) 
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
    conn.close()
