import os
import mimetypes
import humanize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from .database import get_user_data, update_user_data
from .archive_utils import handle_archive, is_archive
from . import logger
from .helper import get_send_function


async def handle_file(
    update: Update, context: ContextTypes.DEFAULT_TYPE, local_mode: bool
) -> None:
    """
    Handles an incoming file from a user, updates user statistics, and sends a confirmation message.

    Args:
        update (Update): The update object containing the message and user information.
        context (ContextTypes.DEFAULT_TYPE): The context object for the current conversation.
        local_mode (bool): A flag indicating whether the bot is running in local mode.

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
    try:
        user_id = update.effective_user.id
        file = update.message.document
        file_size = file.file_size
        file_name = file.file_name

        if is_archive(file_name):
            if not local_mode:
                await update.message.reply_text(
                    "Archives are not supported in non-local mode."
                )
                logger.warning("Archives are not supported in non-local mode.")
                return

            await update.message.reply_text(
                f"Processing archive: '{file_name}'... This may take some time."
            )
            logger.debug(
                "Processing archive: '%s' (%s)",
                file_name,
                humanize.naturalsize(file_size),
            )
            await handle_archive(update, context, file.file_id)
            await update.message.reply_text(f"Archive received: '{file_name}'.")
            return

        logger.debug(
            "Processing file: '%s' (%s)",
            file_name,
            humanize.naturalsize(file_size),
        )
        user_stats = get_user_data(user_id)

        user_stats["total_size"] += file_size
        user_stats["total_download_size"] += file_size
        user_stats["file_count"] += 1

        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type and mime_type.startswith("video"):
            user_stats["streamable"] += 1

        extension = os.path.splitext(file_name)[1].lower()
        user_stats["extension_categories"].setdefault(extension, 0)
        user_stats["extension_categories"][extension] += 1

        update_user_data(user_id, user_stats)
        await update.message.reply_text(
            f"File received: '{file_name}' ({humanize.naturalsize(file_size)})"
        )
    except Exception as e:
        logger.error("Error handling file: %s", e)
        await update.message.reply_text("Error handling file.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Fetches and sends user statistics as a formatted HTML message.

    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains data related to the current context.

    Returns:
        None

    Raises:
        Exception: If there is an error while fetching or sending the user statistics.

    The function retrieves the user statistics such as total file size, total download size, number of files uploaded,
    number of streamable videos, and file extensions. It formats these statistics into an HTML
    message and sends it to the user. If an error occurs during this process, an error message
    is logged and a generic error message is sent to the user.
    """
    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("⌫ Reset Statistics", callback_data="reset")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        send = get_send_function(update)
        user_id = update.effective_user.id
        user_stats = get_user_data(user_id)
        file_count = str(user_stats["file_count"])
        if int(file_count) > 1:
            file_count += " files"
        else:
            file_count += " file"

        msg = (
            f"Total file size: <code>{humanize.naturalsize(user_stats['total_size'])}</code>\n"
            f"Total download size: <code>{humanize.naturalsize(user_stats['total_download_size'])}</code>\n"
            f"Number of files uploaded: <code>{file_count}</code>\n"
            f"Streamable files: <code>{user_stats['streamable']} {"videos" if user_stats['streamable'] > 1 else 'video'}</code>\n"
            "Extensions:\n"
        )
        if not user_stats["extension_categories"]:
            msg += "<code>No files uploaded yet.</code>\n"
        else:
            for ext, count in user_stats["extension_categories"].items():
                msg += (
                    f"<code>{ext}: {count} {"file" if count == 1 else "files"}</code>\n"
                )

        await send(msg, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        logger.error("Error getting stats: %s", e)
        await send("Error getting statistics.", reply_markup=reply_markup)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Resets the user's statistics to default values.

    This function updates the user's data to reset their statistics. It sends
    a confirmation message to the user upon success, or an error message if an
    exception occurs.

    Args:
        update (Update): The update object that contains information about the
                         incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains
                                             information about the current context.

    Returns:
        None
    """
    user_id = update.effective_user.id
    send = get_send_function(update)
    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        update_user_data(
            user_id,
            {
                "total_size": 0,
                "total_download_size": 0,
                "file_count": 0,
                "streamable": 0,
                "extension_categories": {},
            },
        )
        await send("Statistics reset successfully.", reply_markup=reply_markup)
    except Exception as e:
        logger.error("Error resetting stats: %s", e)
        await send("Error resetting statistics.", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a help message with a list of available commands and their descriptions.

    Args:
        update (Update): Incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context of the update.

    Returns:
        None
    """
    send = get_send_function(update)
    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
        [InlineKeyboardButton("⌫ Reset Statistics", callback_data="reset")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send(
        f"Welcome {update.effective_user.first_name} to the file monitoring bot! Here's what you can do:\n"
        "/start - Start the bot and get information on how to use it.\n"
        "/stats - View statistics on uploaded files.\n"
        "/reset - Reset the statistics.\n"
        "/help - Show this help message.\n"
        "You can also send documents and receive summaries on their size and more.",
        reply_markup=reply_markup,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a home page message with buttons for available commands.

    Args:
        update (Update): Incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context of the update.

    Returns:
        None
    """
    keyboard = [
        [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
        [InlineKeyboardButton("⌫ Reset Statistics", callback_data="reset")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    send = get_send_function(update)

    await send(
        f"Welcome {update.effective_user.first_name} to the file monitoring bot! Use the buttons below to navigate.",
        reply_markup=reply_markup,
    )


async def callback_query_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handles callback queries triggered by inline buttons.

    Args:
        update (Update): The update object containing the callback query.
        context (ContextTypes.DEFAULT_TYPE): The context object for the current conversation.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query to avoid a loading state in Telegram.

    match query.data:
        case "stats":
            await stats(update, context)
        case "reset":
            await reset(update, context)
        case "help":
            await help_command(update, context)
        case "start":
            await start_command(update, context)
        case _:
            logger.warning("Unknown action: %s", query.data)
            await query.edit_message_text("Unknown action. Please try again.")
