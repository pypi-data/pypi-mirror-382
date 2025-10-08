import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GROUP_NAME = "default"

STORAGE_PATH = Path(os.getenv("CLIOTP_STORAGE_PATH", Path.home()))
STORAGE_DIR = STORAGE_PATH.joinpath(".cliotp")

PASSWORD_FILE = STORAGE_DIR.joinpath("master-password.txt")

DB_PATH = str(STORAGE_DIR / "cliopt.sqlite3")

STORAGE_DIR.mkdir(exist_ok=True)
