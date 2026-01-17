import hmac
import hashlib
import os
import sys
import json
import glob
from datetime import date

SECRET_KEY = "ARRGGGHHHH"  # KEEP THIS SECRET
APP_ID = "NON_VAT_INCOME_EXPENSE_TAX_TRACKER"


# ================== EXE-SAFE PATH ==================
def get_app_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ================== LICENSE FOLDER ==================
LICENSE_DIR = os.path.join(get_app_root(), "data", "license")
os.makedirs(LICENSE_DIR, exist_ok=True)

LAST_RUN_FILE = os.path.join(LICENSE_DIR, "last_run.json")
VIOLATION_FILE = os.path.join(LICENSE_DIR, "violation.lock")

# ================== LICENSE LOAD ==================
def load_license() -> dict | None:
    """
    Loads the latest license_YYYY-MM-DD.json from data/license
    """
    files = sorted(
        glob.glob(os.path.join(LICENSE_DIR, "license_*.json")),
        reverse=True
    )

    if not files:
        return None

    try:
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def load_last_run() -> dict | None:
    if not os.path.exists(LAST_RUN_FILE):
        return None

    try:
        with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "last_run" not in data or "signature" not in data:
            return None

        expected = sign_last_run(data["last_run"])
        if expected != data["signature"]:
            return None

        return data
    except Exception:
        return None

def save_last_run(run_date: date):
    payload = {
        "last_run": run_date.isoformat(),
        "signature": sign_last_run(run_date.isoformat())
    }

    with open(LAST_RUN_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


# ================== CRYPTO ==================
def sign(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

def sign_last_run(run_date: str) -> str:
    data = f"{APP_ID}|{run_date}"
    return sign(data)


# ================== LICENSE VERIFY ==================
def verify_license(license_data: dict) -> tuple[bool, str]:
    required_keys = ["app_id", "file_name", "expires_at", "signature"]

    for key in required_keys:
        if key not in license_data:
            return False, f"Missing key: {key}"

    if license_data["app_id"] != APP_ID:
        return False, "License not for this application"

    data = (
        f"{license_data['app_id']}|"
        f"{license_data['file_name']}|"
        f"{license_data['expires_at']}"
    )

    expected = sign(data)
    if expected != license_data["signature"]:
        return False, "Invalid license signature"

    expiry = datetime.strptime(
        license_data["expires_at"], "%Y-%m-%d"
    ).date()

    if expiry < date.today():
        return False, "License has expired"

    return True, "License valid"

# ================== ONE-CALL HELPER ==================
from datetime import datetime

def check_license() -> tuple[str, dict | None]:
    """
    Returns:
        status: 'valid', 'expired', 'missing', 'invalid'
        license_data: dict or None
    """
    license_data = load_license()
    if not license_data:
        return "missing", None

    is_valid, message = verify_license(license_data)

    # ⭐ EXTRACT EXPIRY DATE HERE
    try:
        expiry_date = datetime.strptime(
            license_data["expires_at"], "%Y-%m-%d"
        ).date()
    except Exception:
        return "invalid", license_data

    today = date.today()

    last_run = load_last_run()

    if last_run is None and os.path.exists(LAST_RUN_FILE):
        return "invalid", {
            "reason": "License tampering detected"
        }

    if last_run:
        last_date = datetime.strptime(
            last_run["last_run"], "%Y-%m-%d"
        ).date()

        if today < last_date:
            mark_violation("rollback")
            return "warning", {
                "reason": "System date was set backwards. Please restore correct date."
            }

        if last_date > expiry_date:
            return "invalid", {"reason": "License time manipulation detected"}

    if not is_valid:
        if message == "License has expired":
            return "expired", license_data
        return "invalid", license_data

    # ✅ VALID LICENSE
    # expiry_date is now available in license_data
    license_data["_expiry_date"] = expiry_date
    clear_violation()
    save_last_run(today)
    return "valid", license_data

def mark_violation(reason: str):
    payload = {
        "reason": reason,
        "date": date.today().isoformat()
    }
    with open(VIOLATION_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def has_violation() -> bool:
    return os.path.exists(VIOLATION_FILE)


def clear_violation():
    if os.path.exists(VIOLATION_FILE):
        os.remove(VIOLATION_FILE)

