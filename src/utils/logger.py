import logging
import os
from pathlib import Path
from src.utils.config import config

log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(config.LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)

    # File handler
    file_handler = logging.FileHandler(log_dir / f"{name}.log")
    file_handler.setLevel(config.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
