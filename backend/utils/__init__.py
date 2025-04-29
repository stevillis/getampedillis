"""
Constants for file and directory paths used throughout the application.
"""

from pathlib import Path

DATA_DIR: Path = Path("data")

PLAYERS_FOLDER: Path = DATA_DIR / "players"
ACCESSORIES_FOLDER: Path = DATA_DIR / "accs"
STYLES_FOLDER: Path = DATA_DIR / "styles"
ACCS_BY_YEAR_FILE: Path = DATA_DIR / "accs_by_year.xlsx"


def ensure_directories_exist() -> None:
    """Ensure all required directories exist, creating them if necessary."""
    for directory in (PLAYERS_FOLDER, ACCESSORIES_FOLDER, STYLES_FOLDER):
        directory.mkdir(parents=True, exist_ok=True)


ensure_directories_exist()
