"""
This module contains the handlers for various bot commands and messages.
It includes functions to handle files, user statistics, and other
bot interactions.
"""

import mimetypes
import os

import humanize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from . import get_str, logger
from .archive_utils import handle_archive, is_archive
from .database import Database
from .helper import get_send_function

HOME_LABEL = get_str("🏠 Home")
STATS_LABEL = get_str("📊 View Statistics")
RESET_LABEL = get_str("⌫ Reset Statistics")
HELP_LABEL = get_str("🆘 Help")


async def handle_file(
    update: Update, context: ContextTypes.DEFAULT_TYPE, local_mode: bool
) -> None:
    """
    Handles an incoming file from a user, updates user statistics, and sends a
    confirmation message.

    Args:
        - update (Update): The update object containing the message and
        user information.
        - context (ContextTypes.DEFAULT_TYPE): The context object for the
        current conversation.
        - local_mode (bool): A flag indicating whether the bot is
        running in local mode.

    Raises:
        Exception: If there is an error during file handling.

    The function performs the following steps:
    1. Extracts user ID, file, file size, and file name from the update.
    2. Retrieves user statistics using the user ID.
    3. Updates the user's total file size, file count and total download size.
    4. Increments the count of streamable files if the file is a video.
    5. Updates the count of files by their extension category.
    6. Saves the updated user statistics.
    7. Sends a confirmation message to the user with the file name and size.
    8. Logs and sends an error message if an exception occurs.
    """
    if update.effective_user is None:
        return
    if update.message is None:
        return
    if update.message.document is None:
        return

    try:

        user_id = update.effective_user.id
        file = update.message.document
        file_size = file.file_size
        file_name = file.file_name

        if not file_name or not file_size:
            return

        if is_archive(file_name):
            if not local_mode:
                await update.message.reply_text(
                    get_str("Archives are not supported in non-local mode.")
                )
                logger.warning(
                    get_str("Archives are not supported in non-local mode."))
                return

            await update.message.reply_text(
                f"{get_str('Processing archive')}: '{file_name}'... "
                f"{get_str('This may take some time.')}"
            )
            logger.debug(
                f"{get_str("Processing archive")}: '%s' (%s)",
                file_name,
                humanize.naturalsize(file_size),
            )
            try:
                await handle_archive(update, context, file.file_id)
            except ValueError:
                await update.message.reply_text(
                    get_str("Error handling zip file.")
                )
                return
            keyboard = [
                [InlineKeyboardButton(STATS_LABEL, callback_data="stats")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"{get_str("Archive received")}: '{file_name}'.",
                reply_markup=reply_markup,
            )
            return

        logger.debug(
            f"{get_str("Processing file")}: '%s' (%s)",
            file_name,
            humanize.naturalsize(file_size),
        )
        user_stats = Database().get_user_data(user_id)

        user_stats["total_size"] += file_size
        user_stats["total_download_size"] += file_size
        user_stats["file_count"] += 1

        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type and mime_type.startswith("video"):
            user_stats["streamable"] += 1

        extension = os.path.splitext(file_name)[1].lower()
        user_stats["extension_categories"].setdefault(extension, 0)
        user_stats["extension_categories"][extension] += 1

        Database().update_user_data(user_id, user_stats)
        keyboard = [
            [InlineKeyboardButton(STATS_LABEL, callback_data="stats")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"{get_str('File received')}: '{file_name}' "
            f"({humanize.naturalsize(file_size)})",
            reply_markup=reply_markup,
        )
    except (OSError, ValueError) as error:
        logger.error(get_str("Error handling file: %s"), error)
        await update.message.reply_text(get_str("Error handling file."))


async def stats(update: Update) -> None:
    """
    Fetches and sends user statistics as a formatted HTML message.

    Args:
        - update (Update): The update object that contains information about
        the incoming update.

    Returns:
        None

    Raises:
        Exception: If there is an error while fetching or sending
        the user statistics.

    The function retrieves the user statistics such as total file size,
    total download size, number of files uploaded, number of streamable videos,
    and file extensions. It formats these statistics into an HTML message and
    sends it to the user. If an error occurs during this process, an error
    message is logged and a generic error message is sent to the user.
    """
    if update.effective_user is None:
        return

    keyboard = [
        [InlineKeyboardButton(HOME_LABEL, callback_data="start")],
        (
            [InlineKeyboardButton(RESET_LABEL, callback_data="reset")]
            if not Database().is_stats_empty(update.effective_user.id)
            else []
        ),
        [InlineKeyboardButton(HELP_LABEL, callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    send = get_send_function(update)

    try:
        user_id = update.effective_user.id
        user_stats = Database().get_user_data(user_id)
        file_count = str(user_stats["file_count"])
        if int(file_count) > 1:
            file_count += get_str(" files")
        else:
            file_count += get_str(" file")

        msg = (
            f"{get_str('Total file size')}: "
            f"<code>{humanize.naturalsize(user_stats['total_size'])}</code>\n"
            f"{get_str('Total download size')}: "
            f"<code>{humanize.naturalsize(user_stats['total_download_size'])}"
            f"</code>\n"
            f"{get_str('Number of files uploaded')}: <code>{file_count}"
            f"</code>\n"
            f"{get_str('Streamable files')}: "
            f"<code>{user_stats['streamable']} "
        )

        if user_stats["streamable"] > 1:
            msg += f"{get_str('videos')}</code>\n"
        else:
            msg += f"{get_str('video')}</code>\n"

        msg += f"{get_str('Extensions')}:\n"
        if not user_stats["extension_categories"]:
            msg += f"<code>{get_str("No files uploaded yet.")}</code>\n"
        else:
            for ext, count in user_stats["extension_categories"].items():
                msg += f"<code>{ext}: {count} "
                if count == 1:
                    msg += get_str("file")
                else:
                    msg += get_str("files")
                msg += "</code>\n"

        await send(msg, parse_mode="HTML", reply_markup=reply_markup)
    except (OSError, ValueError) as error:
        logger.error(get_str("Error getting stats: %s"), error)
        await send(
            get_str("Error getting statistics."),
            reply_markup=reply_markup
        )


async def reset(update: Update) -> None:
    """
    Resets the user's statistics to default values.

    This function updates the user's data to reset their statistics. It sends
    a confirmation message to the user upon success, or an error message if an
    exception occurs.

    Args:
        - update (Update): The update object that contains information about
        the incoming update.

    Returns:
        None
    """
    if update.effective_user is None:
        return

    user_id = update.effective_user.id
    send = get_send_function(update)
    keyboard = [
        [InlineKeyboardButton(HOME_LABEL, callback_data="start")],
        [InlineKeyboardButton(HELP_LABEL, callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        Database().reset_user_data(user_id)
        await send(
            get_str("Statistics reset successfully."),
            reply_markup=reply_markup
        )
    except (OSError, ValueError) as error:
        logger.error(get_str("Error resetting stats: %s"), error)
        await send(
            get_str("Error resetting statistics."),
            reply_markup=reply_markup
        )


async def help_command(update: Update) -> None:
    """
    Sends a help message with a list of available commands and
    their descriptions.

    Args:
        update (Update): Incoming update.

    Returns:
        None
    """
    if update.effective_user is None:
        return

    send = get_send_function(update)
    keyboard = [
        [InlineKeyboardButton(HOME_LABEL, callback_data="start")],
        [InlineKeyboardButton(STATS_LABEL, callback_data="stats")],
        (
            [InlineKeyboardButton(RESET_LABEL, callback_data="reset")]
            if not Database().is_stats_empty(update.effective_user.id)
            else []
        ),
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send(
        f"{get_str('Welcome')} {update.effective_user.first_name} "
        f"{get_str('to the file monitoring bot! Here\'s what you can do:')}\n"
        "/start - "
        f"{get_str('Start the bot and get information on how to use it.')}\n"
        f"/stats - {get_str('View statistics on uploaded files.')}\n"
        f"/reset - {get_str('Reset the statistics.')}\n"
        f"/help - {get_str('Show this help message.')}\n"
        f"{get_str(
            "You can also send documents and receive summaries "
            "on their size and more."
        )}",
        reply_markup=reply_markup,
    )


async def start_command(update: Update) -> None:
    """
    Sends a home page message with buttons for available commands.

    Args:
        update (Update): Incoming update.

    Returns:
        None
    """
    if update.effective_user is None:
        return

    keyboard = [
        [InlineKeyboardButton(STATS_LABEL, callback_data="stats")],
        (
            [InlineKeyboardButton(RESET_LABEL, callback_data="reset")]
            if not Database().is_stats_empty(update.effective_user.id)
            else []
        ),
        [InlineKeyboardButton(HELP_LABEL, callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    send = get_send_function(update)

    await send(
        f"{get_str('Welcome')} {update.effective_user.first_name} "
        f"{get_str(
            "to the file monitoring bot! "
            "Use the buttons below to navigate."
        )}",
        reply_markup=reply_markup,
    )


async def callback_query_handler(update: Update) -> None:
    """
    Handles callback queries triggered by inline buttons.

    Args:
        - update (Update): The update object containing the callback query.

    Returns:
        None
    """
    query = update.callback_query
    if query is None:
        return

    try:
        await query.answer()
    except (OSError, ValueError) as error:
        logger.error(error)

    match query.data:
        case "stats":
            await stats(update)
        case "reset":
            await reset(update)
        case "help":
            await help_command(update)
        case "start":
            await start_command(update)
        case _:
            logger.warning(get_str("Unknown action: %s"), query.data)
            await query.edit_message_text(
                get_str("Unknown action. Please try again.")
            )
