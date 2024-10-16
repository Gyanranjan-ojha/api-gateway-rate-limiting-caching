"""
Logging configuration for the FastAPI application.

This file sets up logging for critical application events and errors.
"""

import os
import logging

from app.config.settings import env_settings


if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename=env_settings.LOG_FILE_PATH, 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s", 
)

logger = logging.getLogger(__name__)

