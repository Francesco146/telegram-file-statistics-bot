"""
Tests for the Database class.
"""

import os
import sqlite3

import pytest

from telegram_file_statistics_bot.database import Database


@pytest.fixture(scope="module", name="test_db")
def db():
    """Initializes a Database instance for testing.

    Yields:
        Database: A Database instance for testing.
    """
    test_db_path = "test_database.db"
    db_instance = Database(test_db_path)
    db_instance.init_db()
    yield db_instance
    os.remove(test_db_path)


@pytest.fixture(autouse=True)
def clean_db(test_db):
    """Cleans the `user_data` table before each test.

    Args:
        test_db (Database): A Database instance for testing.
    """
    with sqlite3.connect(test_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_data")
        conn.commit()


def test_singleton_pattern(test_db):
    """Tests the singleton pattern of the Database class.

    Args:
        test_db (Database): A Database instance for testing.
    """
    db1 = Database(test_db.db_path)
    db2 = Database(test_db.db_path)
    assert db1 is db2


def test_init_db(test_db):
    """Tests the initialization of the database by checking if the
    `user_data` table is created.

    Args:
        test_db (Database): A Database instance for testing.
    """
    with sqlite3.connect(test_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='user_data'
            """
        )
        table = cursor.fetchone()
    assert table is not None


def test_get_user_data(test_db):
    """Tests the retrieval of user data from the database.

    Args:
        test_db (Database): A Database instance for testing.
    """
    user_id = 1
    user_data = test_db.get_user_data(user_id)
    expected_data = {
        "total_size": 0,
        "total_download_size": 0,
        "file_count": 0,
        "streamable": 0,
        "extension_categories": {},
        "ignored_extensions": [],
    }
    assert user_data == expected_data


def test_reset_user_data(test_db):
    """Tests the resetting of user data in the database.

    Args:
        test_db (Database): A Database instance for testing.
    """
    user_id = 1
    test_db.reset_user_data(user_id)
    user_data = test_db.get_user_data(user_id)
    expected_data = {
        "total_size": 0,
        "total_download_size": 0,
        "file_count": 0,
        "streamable": 0,
        "extension_categories": {},
        "ignored_extensions": [],
    }
    assert user_data == expected_data


def test_update_user_data(test_db):
    """Tests the updating of user data in the database.

    Args:
        test_db (Database): A Database instance for testing.
    """
    user_id = 1
    new_data = {
        "total_size": 100,
        "total_download_size": 50,
        "file_count": 10,
        "streamable": 5,
        "extension_categories": {"pdf": 5, "docx": 5},
        "ignored_extensions": [],
    }
    test_db.update_user_data(user_id, new_data)
    user_data = test_db.get_user_data(user_id)
    assert user_data == new_data


def test_is_stats_empty(test_db):
    """Tests the `is_stats_empty` method of the Database class.

    Args:
        test_db (Database): A Database instance for testing.
    """
    user_id = 1
    assert test_db.is_stats_empty(user_id)
    new_data = {
        "total_size": 100,
        "total_download_size": 50,
        "file_count": 10,
        "streamable": 5,
        "extension_categories": {"pdf": 5, "docx": 5},
    }
    test_db.update_user_data(user_id, new_data)
    assert not test_db.is_stats_empty(user_id)


def test_remove_extensions_from_user_updates_count_and_size(test_db):
    """Test that removing an extension updates both file count and total size correctly."""
    user_id = 42
    new_data = {
        "total_size": 300,
        "total_download_size": 300,
        "file_count": 6,
        "streamable": 0,
        "extension_categories": {
            ".zip": {"count": 2, "size": 100},
            ".mp3": {"count": 4, "size": 200},
        },
        "ignored_extensions": [],
    }
    test_db.update_user_data(user_id, new_data)
    # Remove .mp3 extension
    test_db.remove_extensions_from_user(user_id, [".mp3"])
    user_data = test_db.get_user_data(user_id)
    assert user_data["file_count"] == 2  # Only .zip files remain
    assert user_data["total_size"] == 100  # Only .zip size remains
    assert user_data["total_download_size"] == 100  # Only .zip download size remains
    assert ".mp3" not in user_data["extension_categories"]
    assert user_data["extension_categories"][".zip"]["count"] == 2
    assert user_data["extension_categories"][".zip"]["size"] == 100
