import argparse


def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments for the Telegram Bot for File Statistics.

    Returns:
        argparse.Namespace: A namespace object containing the parsed arguments.

    Arguments:
        -t, --token (str): Bot token (or set TOKEN environment variable).
        -db, --database (str): Path to the SQLite database file (default: "file_statistics.db").
        -d, --debug: Enable debug mode for logging.
    """
    parser = argparse.ArgumentParser(
        description="Telegram Bot for File Statistics",
        epilog="Made with ❤️ by @Francesco146",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        help="Bot token (or set TOKEN environment variable)",
        default=None,
    )
    parser.add_argument(
        "-db",
        "--database",
        type=str,
        help="Path to the SQLite database file",
        default="file_statistics.db",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode for logging",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="telegram-file-statistics-bot v0.9.0",
        help="Show the version of the program",
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="Run the bot in a telegram api bot local server",
        default=False,
    )

    return parser.parse_args()
