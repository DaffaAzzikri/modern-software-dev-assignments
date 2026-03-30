"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment."""

    db_path: Path
    debug: bool

    def get_data_dir(self) -> Path:
        """Get the data directory containing the database."""
        return self.db_path.parent


def get_settings() -> Settings:
    """Return application settings from environment."""
    base = Path(__file__).resolve().parents[1]
    default_db = base / "data" / "app.db"
    db_path_str = os.environ.get("APP_DB_PATH", "")
    db_path = Path(db_path_str) if db_path_str else default_db
    debug = os.environ.get("APP_DEBUG", "").lower() in ("1", "true", "yes")
    return Settings(db_path=db_path, debug=debug)
