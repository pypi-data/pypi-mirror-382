"""Logging configuration utilities for the Chess Tournament Software."""

import logging
import sys
from typing import Optional


def setup_logging(
    quiet: bool = False,
    log_to_file: bool = True,
    file_name: str = "app.log",
    log_level: int = logging.DEBUG,
    datefmt: Optional[str] = "%H:%M:%S",
):
    """
    Configure global application logging.

    Args:
        quiet (bool): If True, console logs only WARNING and above.
        log_to_file (bool): If True, logs will also be written to a file.
        file_name (str): Path to the log file.
        log_level (int): Base level for root logger.
        datefmt (str): Format for timestamps in log entries.

    Example:
        setup_logging(quiet=True, log_to_file=False)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Prevent duplicated handlers on multiple calls
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt=datefmt,
    )

    # Console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING if quiet else logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Optional file output
    if log_to_file:
        file_handler = logging.FileHandler(file_name, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Global exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger().error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = handle_exception
