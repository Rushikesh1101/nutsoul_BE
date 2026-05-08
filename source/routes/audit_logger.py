import os
from datetime import datetime

def write_audit_log(action, user_email=None, status="SUCCESS", message=""):
    today = datetime.utcnow().strftime('%Y-%m-%d')
    log_dir = "logs/audit"
    os.makedirs(log_dir, exist_ok=True)

    log_filename = f"{today}_audit.log"
    log_path = os.path.join(log_dir, log_filename)

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    log_entry = f"[{timestamp}] ACTION:{action} USER:{user_email or 'N/A'} STATUS:{status} MESSAGE:{message}\n"

    with open(log_path, "a") as f:
        f.write(log_entry)
