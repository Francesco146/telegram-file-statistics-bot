"""
This module provides utility functions for handling archive files.
It includes functions to process and extract archive files,
and update user statistics.
"""

import mimetypes
import os
import tempfile
import zipfile
from typing import Dict

import humanize
from telegram import Update
from telegram.ext import ContextTypes

from . import get_str, logger
from .database import Database


async def handle_archive(
    update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str
) -> None:
    """
    Handles the processing of an archive file sent by the user.

    This function performs the following steps:
    1. Retrieves the user ID and user statistics.
    2. Downloads the archive file to the local drive.
    3. Extracts the contents of the archive to a temporary directory.
    4. Iterates through the extracted files to update user statistics:
        - Total size of files.
        - Count of files.
        - Count of streamable video files.
        - Count of files by extension category.
    5. Updates the user statistics in the database.
    6. Sends a message to the user for each file received.
    7. Updates the total download size of the archive in user statistics.

    The difference between total size and total download size is that
    the total size represents the cumulative size of all individual files,
    while the total download size represents the size of the archive file
    itself. This one is useful to track the amount of data that the user has
    to download in order to get the files.

    Args:
        - update (telegram.Update): The update object that contains information
        about the incoming update.
        - context (telegram.ext.CallbackContext): The context object that
        contains data related to the callback.
        file_id (str): The ID of the file to be processed.

    Raises:
        Exception: If an error occurs during the processing of the
        archive file.
    """
    if update.effective_user is None:
        return
    if update.message is None:
        return

    try:
        user_id = update.effective_user.id
        user_stats = Database()[user_id]

        file = await context.bot.get_file(file_id)

        if file.file_path is None:
            raise ValueError(get_str("File path is None"))

        archive_absolute_path = get_archive_absolute_path(file.file_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            extract_archive(archive_absolute_path, temp_dir)

            await process_extracted_files(temp_dir, user_id, user_stats, update)

            user_stats["total_download_size"] += os.path.getsize(archive_absolute_path)

            Database()[user_id] = user_stats
    except (zipfile.BadZipFile, OSError, ValueError) as error:
        logger.error(get_str("Error handling zip file: %s"), error)
        raise error


def get_archive_absolute_path(file_path: str) -> str:
    """Get the absolute path of the archive file.

    Args:
        file_path (str): The URL path of the archive file.

    Returns:
        str: The absolute path of the archive file.
    """
    split_path = file_path.split("/")
    # api/telegram-bot-api-data/<token>/documents/<file_name>
    base_dir = os.path.join("api/telegram-bot-api-data", split_path[-3])
    return os.path.join(base_dir, split_path[-2], split_path[-1])


def extract_archive(archive_path: str, temp_dir: str) -> None:
    """Extract the contents of the archive file to a temporary directory.

    Args:
        archive_path (str): The path to the archive file.
        temp_dir (str): The path to the temporary directory where the contents
        of the archive will be extracted.
    """
    with zipfile.ZipFile(archive_path, "r") as archive_ref:
        archive_ref.extractall(temp_dir)


async def process_extracted_files(
    temp_dir: str, user_id: int, user_stats: Dict, update: Update
) -> None:
    """Process the extracted files from the archive.

    Args:
        - temp_dir (str): The path to the temporary directory containing the
        extracted files.
        - user_id (int): The ID of the user who sent the archive file.
        - user_stats (dict): The user statistics to be updated.
        - update (Update): The update object containing information about the
        incoming update.
    """
    if update.message is None:
        return

    ignored = user_stats.get("ignored_extensions", [])
    for root, _, files in os.walk(temp_dir):
        for file in files:
            extension = os.path.splitext(file)[1].lower()
            if extension in ignored:
                logger.info(
                    "File '%s' inside archive ignored due to its extension (%s).",
                    file,
                    extension,
                )
                continue
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            logger.debug(
                f"{get_str('Processing file')}: '%s' (%s)",
                file,
                humanize.naturalsize(file_size),
            )

            update_user_statistics(user_stats, file, file_size)
            Database()[user_id] = user_stats
            await update.message.reply_text(
                f"{get_str('File received via archive')}: '{file}' "
                f"({humanize.naturalsize(file_size)})."
            )


def update_user_statistics(user_stats: Dict, file: str, file_size: int) -> None:
    """Update the user statistics based on the processed file.

    Args:
        - user_stats (dict): The user statistics to be updated.
        - file (str): The name of the processed file.
        - file_size (int): The size of the processed file.
    """
    user_stats["total_size"] += file_size
    user_stats["file_count"] += 1

    mime_type, _ = mimetypes.guess_type(file)
    if mime_type and mime_type.startswith("video"):
        user_stats["streamable"] += 1

    extension = os.path.splitext(file)[1].lower()
    user_stats["extension_categories"].setdefault(extension, 0)
    user_stats["extension_categories"][extension] += 1


def is_archive(file_name: str) -> bool:
    """
    Check if the given file name has an archive extension.

    Args:
        file_name (str): The name of the file to check.

    Returns:
        bool: True if the file name ends with an archive extension,
        False otherwise.
    """
    return file_name.lower().endswith(("zip"))  # add more extensions if needed
