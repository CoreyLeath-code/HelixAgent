# src/utils/logger.py

"""
Logger Utility for HelixAgent
-----------------------------
Provides centralized structured logging with loguru.
Ensures consistent, professional logs across all modules.
"""

import sys

from loguru import logger


def setup_logger(log_file: str = "logs/helixagent.log", level: str = "INFO"):
    """
    Configure the logger.
    
    Args:
        log_file (str): Path to log file.
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Remove default logger to reconfigure
    logger.remove()

    # Console output (colorized)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
        level=level,
    )

    # File output
    logger.add(
        log_file,
        rotation="5 MB",
        retention="10 days",
        level=level,
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info("Logger initialized.")
    return logger


# Example usage:
# from utils.logger import setup_logger
# log = setup_logger()
# log.info("HelixAgent started successfully.")
