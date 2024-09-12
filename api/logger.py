"""
Logging configuration for the FastAPI application.

This file sets up logging for critical application events and errors. Logs are stored in a file specified
by environment variables, and logging is configured to capture INFO level and higher logs.
"""

import os
import logging

from api.config import env_settings


# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging settings to capture errors and critical information
logging.basicConfig(
    filename=env_settings.LOG_FILE_PATH,  # Log file path from environment settings
    level=logging.INFO,  # Log level: INFO and higher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format including timestamp
)

# Create a logger instance
logger = logging.getLogger(__name__)

# Example usage in code: logger.info("Informational message")
# Performance: Logging operations are I/O bound, but kept at minimal levels to avoid performance degradation.
