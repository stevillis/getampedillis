"""
Constants for file and directory paths used throughout the application.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")
SHOW_TROLL_INTRO = os.getenv("SHOW_TROLL_INTRO")

DATA_DIR: Path = Path("data")

PLAYERS_FOLDER: Path = DATA_DIR / "players"
ACCESSORIES_FOLDER: Path = DATA_DIR / "accs"
STYLES_FOLDER: Path = DATA_DIR / "styles"
ACCS_BY_YEAR_FILE: Path = DATA_DIR / "accs_by_year.xlsx"
TIRIRICAS_PATH: Path = DATA_DIR / "tiririca.png"


def ensure_directories_exist() -> None:
    """Ensure all required directories exist, creating them if necessary."""
    for directory in (PLAYERS_FOLDER, ACCESSORIES_FOLDER, STYLES_FOLDER):
        directory.mkdir(parents=True, exist_ok=True)


ensure_directories_exist()
