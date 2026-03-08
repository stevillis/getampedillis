"""
Constants for file and directory paths used throughout the application.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR: Path = Path("data")

PLAYERS_FOLDER: Path = DATA_DIR / "players"
ACCESSORIES_FOLDER: Path = DATA_DIR / "accs"
STYLES_FOLDER: Path = DATA_DIR / "styles"
ACCS_BY_YEAR_FILE: Path = DATA_DIR / "accs_by_year.xlsx"

GETAMPEDVIVE_GEMINI_API_KEY = os.environ.get("GETAMPEDVIVE_GEMINI_API_KEY")
GETAMPEDVIVE_GEMINI_MODEL = os.environ.get(
    "GETAMPEDVIVE_GEMINI_MODEL", "gemini-3.1-flash-lite-preview"
)
GETAMPEDVIVE_GEMINI_EMBEDDING_MODEL = os.environ.get(
    "GETAMPEDVIVE_GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def ensure_directories_exist() -> None:
    """Ensure all required directories exist, creating them if necessary."""
    for directory in (PLAYERS_FOLDER, ACCESSORIES_FOLDER, STYLES_FOLDER):
        directory.mkdir(parents=True, exist_ok=True)


ensure_directories_exist()
