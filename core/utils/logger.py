"""Centralized logging module for the Unified Automation Framework.

Provides rich console logging and rotating file logs.
Works seamlessly with Loguru or standard Python logging as fallback.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "framework.log"

try:
    from loguru import logger

    # Remove default handler and configure custom sinks
    logger.remove()

    # Console output with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=os.getenv("LOG_LEVEL", "INFO"),
        colorize=True,
    )

    # File output with rotation
    logger.add(
        str(LOG_FILE),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="14 days",
        encoding="utf-8",
    )

    get_logger = lambda name="framework": logger.bind(name=name)

except ImportError:
    # Standard library fallback if loguru is not yet installed
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )

    def get_logger(name: str = "framework") -> logging.Logger:
        return logging.getLogger(name)


# Export a global logger instance
framework_logger = get_logger("framework")
