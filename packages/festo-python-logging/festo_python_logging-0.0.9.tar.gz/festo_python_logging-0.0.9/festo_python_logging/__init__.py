import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from festo_python_logging.formatter import AlignedFormatter


def configure_logging(
    verbose: bool = False,
    silence: Optional[List[str]] = None,
    log_dir: Optional[str] = None,
) -> None:
    """Configures logging for the application.

    Args:
        verbose (bool): If True, sets the logging level to DEBUG.
        silence (Optional[List[str]]): A list of logger names to silence by setting their level to ERROR.
        log_dir (Optional[str]): Directory path where log files will be saved.
            If None, logging to file is disabled.

    Returns:
        None

    """
    # Define formatters for stdout and file logging
    stdout_formatter = AlignedFormatter()
    file_formatter = logging.Formatter(
        fmt="{relativeCreated:13.2f} {levelname:>8} {name:>35.35}:{lineno:4d} │  {message}",
        style="{",
    )

    # Set up the stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_formatter)

    # Create the handlers list and add the stdout handler
    handlers = [stdout_handler]

    # If a log file path is provided, set up the file handler
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(log_dir / f"log_{timestamp}.log")
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure the basic logging setup
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, handlers=handlers)
    logging.info("Logging configured")

    # Silence specified loggers if requested
    if silence:
        for logger_name in silence:
            logging.getLogger(logger_name).setLevel(logging.ERROR)


__all__ = ["configure_logging"]
