from typing import Callable

from telegram import Update

from . import get_str


def get_send_function(update: Update) -> Callable:
    """
    Returns the appropriate send function based on the update type.

    Args:
        update (Update): The update object containing the message.

    Returns:
        callable: The appropriate send function based on the update type.
        If the update is a message,
        returns the reply_text function.
        If the update is a callback query,
        returns the edit_message_text function.
    """
    if update.callback_query:
        return update.callback_query.edit_message_text
    else:
        if update.message:
            return update.message.reply_text
        else:
            raise ValueError(
                get_str("Update does not contain a message or callback query")
            )
