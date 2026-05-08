import logging


def setup_logger():

    logger = logging.getLogger("app")

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
