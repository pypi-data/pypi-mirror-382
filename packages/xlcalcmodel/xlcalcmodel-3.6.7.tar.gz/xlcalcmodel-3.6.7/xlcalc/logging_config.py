import logging
from logging.handlers import RotatingFileHandler

LOG_FILENAME = "xlcalcmodel.log"
MAX_BYTES = 100_000_000  # 100MB per log file
BACKUP_COUNT = 5       # Keep 5 backups

def setup_logging():
    """
    Set up a rotating file handler and remove any console handlers.
    Call this once at program start.
    """
    # Get the root logger (or use a named logger if preferred).
    root_logger = logging.getLogger()
    #LOG LEVEL CAN BE CHANGED
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers (e.g., default console)
    root_logger.handlers.clear()

    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILENAME,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT
    )
    #LOG LEVEL CAN BE CHANGED
    file_handler.setLevel(logging.INFO)

    # Customize format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add to root logger
    root_logger.addHandler(file_handler)
