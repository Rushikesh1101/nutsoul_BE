import logging
from datetime import datetime

audit_logger = logging.getLogger("audit")

if not audit_logger.handlers:
    audit_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s [AUDIT] %(message)s")

    console_handler.setFormatter(formatter)

    audit_logger.addHandler(console_handler)


def write_audit_log(action, user_email=None, status="SUCCESS", message=""):

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    log_entry = (
        f"ACTION:{action} "
        f"USER:{user_email or 'N/A'} "
        f"STATUS:{status} "
        f"MESSAGE:{message} "
        f"TIME:{timestamp}"
    )

    audit_logger.info(log_entry)
