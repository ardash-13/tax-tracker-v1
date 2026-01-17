import os
import sys


def get_app_data_dir():
    """
    Returns the base data directory beside the .exe (or script when running as .py)
    """
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))

    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


# ================== GLOBAL PATHS ==================
DATA_DIR = get_app_data_dir()

BACKUP_DIR = os.path.join(DATA_DIR, "backups")
# DB_DIR = os.path.join(DATA_DIR, "database")
LICENSE_DIR = os.path.join(DATA_DIR, "license")

# Ensure subfolders exist
os.makedirs(BACKUP_DIR, exist_ok=True)
# os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(LICENSE_DIR, exist_ok=True)
