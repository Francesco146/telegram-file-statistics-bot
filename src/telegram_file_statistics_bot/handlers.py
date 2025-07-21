"""
This module contains the handlers for various bot commands and messages.
It includes functions to handle files, user statistics, and other bot interactions.
"""

import mimetypes
import os

import humanize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from . import get_str, logger, nget_str
from .archive_utils import handle_archive, is_archive
from .database import Database
from .helper import get_send_function

HOME_LABEL = get_str("🏠 Home")
STATS_LABEL = get_str("📊 View Statistics")
RESET_LABEL = get_str("⌫ Reset Statistics")
HELP_LABEL = get_str("🆘 Help")


async def ignore_extensions_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Allows the user to add, remove, or list ignored file extensions.
    Usage:
        /ignore_extensions .exe .mp3   # Add to ignore list
        /ignore_extensions -rm .exe    # Remove from ignore list
        /ignore_extensions             # List ignored extensions
    """
    if update.effective_user is None:
        return
    user_id = update.effective_user.id
    send = get_send_function(update)
    args = context.args if hasattr(context, "args") else []
    db = Database()
    user_stats = db.get_user_data(user_id)
    ignored: list[str] = user_stats.get("ignored_extensions", [])

    if not args:
        if ignored:
            await send(f"Ignored extensions: {', '.join(ignored)}")
        else:
            await send("No ignored extensions set.")
        return

    if args[0] == "-rm":
        # Remove extensions
        removed = []
        for ext in args[1:]:
            ext = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            if ext in ignored:
                ignored.remove(ext)
                removed.append(ext)
        db.update_user_data(user_id, {**user_stats, "ignored_extensions": ignored})
        if removed:
            await send(f"Removed from ignore list: {', '.join(removed)}")
        else:
            await send("No matching extensions found in ignore list.")
        return

    # Add extensions
    added = []
    for ext in args:
        ext = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        if ext not in ignored:
            ignored.append(ext)
            added.append(ext)
    db.update_user_data(user_id, {**user_stats, "ignored_extensions": ignored})
    if added:
        await send(f"Added to ignore list: {', '.join(added)}")
    else:
        await send("No new extensions added.")


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

    if not (update.effective_user and update.message and update.message.document):
        return

    try:
        user_id = update.effective_user.id
        file = update.message.document
        file_size = file.file_size
        file_name = file.file_name

        if not file_name or not file_size:
            return

        # Check ignored extensions
        user_stats = Database().get_user_data(user_id)
        ignored = user_stats.get("ignored_extensions", [])
        extension = os.path.splitext(file_name)[1].lower()
        if extension in ignored:
            await update.message.reply_text(
                f"File '{file_name}' ignored due to its extension ({extension})."
            )
            return

        if is_archive(file_name):
            if not local_mode:
                await update.message.reply_text(
                    get_str("Archives are not supported in non-local mode.")
                )
                logger.warning(get_str("Archives are not supported in non-local mode."))
                return

            await update.message.reply_text(
                f"{get_str('Processing archive')}: '{file_name}'... "
                f"{get_str('This may take some time.')}"
            )
            logger.debug(
                f"{get_str('Processing archive')}: '%s' (%s)",
                file_name,
                humanize.naturalsize(file_size),
            )
            try:
                await handle_archive(update, context, file.file_id)
            except ValueError:
                await update.message.reply_text(get_str("Error handling zip file."))
                return
            keyboard = [
                [InlineKeyboardButton(STATS_LABEL, callback_data="stats")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"{get_str('Archive received')}: '{file_name}'.",
                reply_markup=reply_markup,
            )
            return

        logger.debug(
            f"{get_str('Processing file')}: '%s' (%s)",
            file_name,
            humanize.naturalsize(file_size),
        )

        user_stats["total_size"] += file_size
        user_stats["total_download_size"] += file_size
        user_stats["file_count"] += 1

        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type and mime_type.startswith("video"):
            user_stats["streamable"] += 1
        ext_cats = user_stats["extension_categories"]
        if extension not in ext_cats or not isinstance(ext_cats[extension], dict):
            ext_cats[extension] = {"count": 0, "size": 0}
        ext_cats[extension]["count"] += 1
        ext_cats[extension]["size"] += file_size
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

        file_count = user_stats["file_count"]
        file_count_str = nget_str("%d file", "%d files", file_count) % file_count

        streamable_count = user_stats["streamable"]
        streamable_count_str = (
            nget_str("%d video", "%d videos", streamable_count) % streamable_count
        )

        msg_parts = [
            f"{get_str('Total file size: ')}"
            f"<code>{humanize.naturalsize(user_stats['total_size'])}</code>",
            f"{get_str('Total download size: ')}"
            f"<code>{humanize.naturalsize(user_stats['total_download_size'])}</code>",
            f"{get_str('Number of files uploaded: ')}<code>{file_count_str}</code>",
            f"{get_str('Streamable files: ')}<code>{streamable_count_str}</code>",
            f"{get_str('File extensions:')}",
        ]

        if not user_stats["extension_categories"]:
            msg_parts.append(f"<code>{get_str('No files uploaded yet.')}</code>")
        else:
            for ext, info in user_stats["extension_categories"].items():
                if isinstance(info, dict):
                    count = info.get("count", 0)
                    size = info.get("size", 0)
                    msg_parts.append(
                        f"<code>{ext}: {nget_str('%d file', '%d files', count) % count} ({humanize.naturalsize(size)})</code>"
                    )
                else:
                    # fallback for legacy data
                    msg_parts.append(
                        f"<code>{ext}: {nget_str('%d file', '%d files', info) % info}</code>"
                    )

        msg = "\n".join(msg_parts)

        await send(msg, parse_mode="HTML", reply_markup=reply_markup)
    except (OSError, ValueError) as error:
        logger.error(get_str("Error getting stats: %s"), error)
        await send(get_str("Error getting statistics."), reply_markup=reply_markup)


# Remove extension statistics command
async def remove_extensions_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Allows the user to remove extension statistics from their own data.
    Usage:
        /remove_extensions .exe .mp3   # Remove stats for .exe and .mp3
        /remove_extensions             # List current extension stats
    """
    if update.effective_user is None:
        return
    user_id = update.effective_user.id
    send = get_send_function(update)
    args = context.args if hasattr(context, "args") else []
    db = Database()
    user_stats = db.get_user_data(user_id)
    ext_cats = user_stats.get("extension_categories", {})

    if not args:
        if ext_cats:
            msg = "Current extension stats:\n"
            for ext, info in ext_cats.items():
                if isinstance(info, dict):
                    msg += f"{ext}: {info.get('count', 0)} files, {humanize.naturalsize(info.get('size', 0))}\n"
                else:
                    msg += f"{ext}: {info} files\n"
            await send(msg.strip())
        else:
            await send("No extension statistics found.")
        return

    # Remove specified extensions
    extensions = [
        ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in args
    ]
    db.remove_extensions_from_user(user_id, extensions)
    await send(f"Removed stats for: {', '.join(extensions)}")


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
        await send(get_str("Statistics reset successfully."), reply_markup=reply_markup)
    except (OSError, ValueError) as error:
        logger.error(get_str("Error resetting stats: %s"), error)
        await send(get_str("Error resetting statistics."), reply_markup=reply_markup)


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

    first_name = update.effective_user.first_name

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
        f"{get_str("Welcome %s to the file monitoring bot! Here's what you can do:") % first_name}\n\n"
        "/start - "
        f"{get_str('Start the bot and get information on how to use it.')}\n"
        f"/stats - {get_str('View statistics on uploaded files.')}\n"
        f"/reset - {get_str('Reset the statistics.')}\n"
        f"/ignore_extensions - {get_str('Add, remove, or list ignored file extensions. Example: /ignore_extensions .exe .mp3 or /ignore_extensions -rm .exe')}\n"
        f"/help - {get_str('Show this help message.')}\n"
        f"{get_str('You can also send documents and receive summaries on their size and more.')}",
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

    first_name = update.effective_user.first_name

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
        f"{get_str('Welcome %s to the file monitoring bot! Use the buttons below to navigate.') % first_name}",
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
            await query.edit_message_text(get_str("Unknown action. Please try again."))
