"""
Logging configuration for the FastAPI application.
"""

# import os
# import logging
# from logging.handlers import TimedRotatingFileHandler
# from datetime import datetime
# from typing import Generator


# class LoggerManager:
#     def __init__(self, logger_name: str, batch_size: int = 10):
#         """
#         Initializes the Logger with a logger, a batch size for logs,
#         and a global log buffer.

#         Args:
#             logger_name (str): The name of the logger.
#             batch_size (int): The number of logs to process in each batch.
#         """
#         self.logger = logging.getLogger(logger_name)
#         self.batch_size = batch_size
#         self.log_buffer: list[tuple[str, str]] = []
#         self.configure_logger()

#     def configure_logger(self):
#         """Sets up the logger with a TimedRotatingFileHandler."""
#         if not os.path.exists('logs'):
#             os.makedirs('logs')

#         log_filename = f"logs/{datetime.now().strftime('%d-%m-%Y')}.log"
#         file_handler = TimedRotatingFileHandler(
#             log_filename,
#             when="midnight",
#             interval=1,
#             backupCount=7  # Keep logs for the last 7 days
#         )
#         file_handler.suffix = "%d-%m-%Y"
#         log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#         file_handler.setFormatter(log_formatter)

#         self.logger.setLevel(logging.INFO)
#         self.logger.addHandler(file_handler)

#     def add_log_to_buffer(self, level: str, message: str):
#         """Adds a log message with its level to the buffer."""
#         self.log_buffer.append((level.lower(), message))
#         if len(self.log_buffer) >= self.batch_size:
#             self.write_logs_in_batches()

#     def batch_log_processor(self) -> Generator[list[tuple[str, str]], None, None]:
#         """Generator to process logs in batches."""
#         batch = []
#         for log in self.log_buffer:
#             batch.append(log)
#             if len(batch) == self.batch_size:
#                 yield batch
#                 batch = []
#         if batch:
#             yield batch

#     def write_logs_in_batches(self):
#         """Writes buffered logs in batches to the log file."""
#         for log_batch in self.batch_log_processor():
#             for level, message in log_batch:
#                 if level == "info":
#                     self.logger.info(message)
#                 elif level == "warning":
#                     self.logger.warning(message)
#                 elif level == "error":
#                     self.logger.error(message)
#                 else:
#                     self.logger.critical(message)

#         self.log_buffer = []  # Clear the buffer after writing


# # Instantiate the Logger
# logger = LoggerManager("api_logger")

import os
import logging
from datetime import datetime


class LoggerManager:
    def __init__(self, logger_name: str):
        """
        Initializes the Logger with a logger.

        Args:
            logger_name (str): The name of the logger.
        """
        self.logger = logging.getLogger(logger_name)
        self.configure_logger()

    def configure_logger(self):
        """Sets up the logger with a FileHandler."""
        if not os.path.exists('logs'):
            os.makedirs('logs')

        log_filename = f"logs/{datetime.now().strftime('%d-%m-%Y')}.log"
        file_handler = logging.FileHandler(log_filename)
        log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(log_formatter)

        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def add_log_to_buffer(self, level: str, message: str):
        """Writes a log message to the log file immediately."""
        self.write_logs_immediately(level, message)

    def write_logs_immediately(self, level: str, message: str):
        """Writes a log message to the log file immediately."""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.critical(message)

        # Flush the handler to ensure the log is written immediately
        for handler in self.logger.handlers:
            handler.flush()

# Instantiate the Logger
logger = LoggerManager("api_logger")