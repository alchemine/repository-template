"""Logging module."""

from pathlib import Path
from datetime import datetime
from logging import INFO, Logger, getLogger, Formatter, StreamHandler, FileHandler

from config import LOG_DIR


class DateBasedFileHandler(FileHandler):
    """File handler that uses date-based file names (YYYY-MM-DD.log)."""

    def __init__(self, log_dir: Path, encoding: str = "utf-8"):
        """Initialize date-based file handler.

        Args:
            log_dir: Directory where log files will be stored
            encoding: File encoding (default: utf-8)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.encoding = encoding
        self.current_date = None
        self.current_file = None
        super().__init__(self._get_current_log_file(), encoding=encoding)

    def _get_current_log_file(self) -> str:
        """Get log file path for current date."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.current_date:
            self.current_date = current_date
            self.current_file = str(self.log_dir / f"{current_date}.log")
        return self.current_file

    def emit(self, record):
        """Emit a record, checking if date has changed."""
        # Check if date has changed and update file if necessary
        new_file = self._get_current_log_file()
        if new_file != self.baseFilename:
            # Close old file and open new one
            self.close()
            self.baseFilename = new_file
            self.stream = self._open()
        super().emit(record)


def get_logger(name: str, level: int = INFO) -> Logger:
    """Get logger with both file and console handlers."""
    logger = getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Configure format
    if name.endswith("timer"):
        fmt = "%(asctime)s | %(message)s"
    else:
        fmt = '%(asctime)s | %(levelname)-5s | %(message)s | File "%(pathname)s", line %(lineno)d, in %(funcName)s'

    formatter = Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # File handler with date-based file naming
    file_handler = DateBasedFileHandler(LOG_DIR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
