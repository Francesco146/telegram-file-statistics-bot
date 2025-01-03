import os
import mimetypes
import tempfile
import humanize
import zipfile
from telegram import Update
from telegram.ext import ContextTypes
from .database import get_user_data, update_user_data
from . import logger, _


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

    The difference between total size and total download size is that the total size
    represents the cumulative size of all individual files, while the total download size
    represents the size of the archive file itself. This one is useful to track the amount
    of data that the user has to download in order to get the files.

    Args:
        update (telegram.Update): The update object that contains information about the incoming update.
        context (telegram.ext.CallbackContext): The context object that contains data related to the callback.
        file_id (str): The ID of the file to be processed.

    Raises:
        Exception: If an error occurs during the processing of the archive file.
    """
    try:
        user_id = update.effective_user.id
        user_stats = get_user_data(user_id)

        file = await context.bot.get_file(file_id)

        split_path = file.file_path.split("/")
        # api/telegram-bot-api-data/<token>/documents/<file_name>
        base_dir = os.path.join("api/telegram-bot-api-data", split_path[-3])
        archive_absolute_path = os.path.join(base_dir, split_path[-2], split_path[-1])
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(archive_absolute_path, "r") as archive_ref:
                archive_ref.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    logger.debug(
                        _("Processing file: '%s' (%s)"),
                        file,
                        humanize.naturalsize(file_size),
                    )

                    user_stats["total_size"] += file_size
                    user_stats["file_count"] += 1

                    mime_type = mimetypes.guess_type(file)[0]
                    if mime_type and mime_type.startswith("video"):
                        user_stats["streamable"] += 1

                    extension = os.path.splitext(file)[1].lower()
                    user_stats["extension_categories"].setdefault(extension, 0)
                    user_stats["extension_categories"][extension] += 1

                    update_user_data(user_id, user_stats)
                    await update.message.reply_text(
                        f"{_("File received via archive")}: '{file}' ({humanize.naturalsize(file_size)})."
                    )

            user_stats["total_download_size"] += os.path.getsize(archive_absolute_path)
            update_user_data(user_id, user_stats)
    except Exception as e:
        logger.error(_("Error handling zip file: %s"), e)
        await update.message.reply_text(_("Error handling zip file."))


def is_archive(file_name: str) -> bool:
    """
    Check if the given file name has an archive extension.

    Args:
        file_name (str): The name of the file to check.

    Returns:
        bool: True if the file name ends with an archive extension, False otherwise.
    """
    return file_name.lower().endswith(("zip"))  # add more extensions if needed
