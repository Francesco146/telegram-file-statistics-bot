import os
import mimetypes
import humanize
from telegram import Update
from telegram.ext import ContextTypes
from .database import get_user_data, update_user_data
from . import logger


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles an incoming file from a user, updates user statistics, and sends a confirmation message.

    Args:
        update (Update): The update object containing the message and user information.
        context (ContextTypes.DEFAULT_TYPE): The context object for the current conversation.

    Raises:
        Exception: If there is an error during file handling.

    The function performs the following steps:
    1. Extracts user ID, file, file size, and file name from the update.
    2. Retrieves user statistics using the user ID.
    3. Updates the user's total file size and file count (excluding .zip files).
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

        user_stats = get_user_data(user_id)

        user_stats["total_size"] += file_size
        user_stats["file_count"] += 1 if not file_name.lower().endswith(".zip") else 0

        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type and mime_type.startswith("video"):
            user_stats["streamable"] += 1

        extension = os.path.splitext(file_name)[1].lower()
        user_stats["extension_categories"].setdefault(extension, 0)
        user_stats["extension_categories"][extension] += 1

        update_user_data(user_id, user_stats)
        await update.message.reply_text(
            f"File ricevuto: '{file_name}' ({humanize.naturalsize(file_size)})."
        )
    except Exception as e:
        logger.error("Error handling file: %s", e)
        await update.message.reply_text("Errore durante l'elaborazione del file.")


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

    The function retrieves the user statistics such as total file size, number of files uploaded,
    number of streamable videos, and file extensions. It formats these statistics into an HTML
    message and sends it to the user. If an error occurs during this process, an error message
    is logged and a generic error message is sent to the user.
    """
    try:
        user_id = update.effective_user.id
        user_stats = get_user_data(user_id)
        file_count = str(user_stats["file_count"])
        if int(file_count) > 1:
            file_count += " files"
        else:
            file_count += " file"

        msg = (
            f"Dimensione totale dei file: <code>{humanize.naturalsize(user_stats['total_size'])}</code>\n"
            f"Numero di file caricati: <code>{file_count}</code>\n"
            f"File riproducibili in streaming: <code>{user_stats['streamable']} video</code>\n"
            "Estensioni:\n"
        )
        if not user_stats["extension_categories"]:
            msg += "<code>Nessuna estensione trovata</code>\n"
        else:
            for ext, count in user_stats["extension_categories"].items():
                msg += f"<code>{ext}: {count}</code>\n"

        await update.message.reply_html(msg)
    except Exception as e:
        logger.error("Error getting stats: %s", e)
        await update.message.reply_text("Errore durante il recupero delle statistiche.")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Resets the user's statistics to default values.

    This function updates the user's data to reset their statistics, including
    total size, file count, streamable count, and extension categories. It sends
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
    try:
        update_user_data(
            user_id,
            {
                "total_size": 0,
                "file_count": 0,
                "streamable": 0,
                "extension_categories": {},
            },
        )
        await update.message.reply_text("Statistiche reimpostate con successo.")
    except Exception as e:
        logger.error("Error resetting stats: %s", e)
        await update.message.reply_text(
            "Errore durante il ripristino delle statistiche."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a help message with a list of available commands and their descriptions.

    Args:
        update (Update): Incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context of the update.

    Returns:
        None
    """
    await update.message.reply_text(
        f"Benvenuto {update.effective_user.first_name} nel bot per il monitoraggio dei file! Ecco cosa puoi fare:\n"
        "/start - Avvia il bot e ricevi informazioni su come usarlo.\n"
        "/stats - Visualizza le statistiche sui file caricati.\n"
        "/reset - Reimposta le statistiche.\n"
        "/help - Mostra questo messaggio di aiuto.\n"
        "Puoi anche inviare documenti e ricevere riepiloghi sulla loro dimensione e altro."
    )
