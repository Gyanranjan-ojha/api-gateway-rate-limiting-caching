"""
Logging configuration for the FastAPI application.
"""

import logging

from api.config import env_settings


# ____Logging Configuration____
# Configure the logging settings to capture critical errors and log them to a file.
logging.basicConfig(
    filename=env_settings.LOG_FILE_PATH,  # Path to log file
    level=logging.ERROR,  # Log level: Only capture ERROR or higher
    format='%(asctime)s:%(levelname)s:%(message)s'  # Log format with timestamp and log level
)

# Create a logger instance
logger = logging.getLogger(__name__)

# Example usage in code: logger.error("An error occurred")
