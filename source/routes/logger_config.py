import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logger(log_dir='logs/app'):
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, 'app.log')  # This becomes the base name

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Rotates every midnight, keeps 7 days of logs
    file_handler = TimedRotatingFileHandler(log_path, when='midnight', interval=1, backupCount=7, utc=True)
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"  # Output format: app.log.2025-07-02

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
