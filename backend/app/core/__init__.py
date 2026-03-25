"""
Core application infrastructure module.
Includes configuration, database setup, and other foundational components.
"""

from app.core.config import settings
from app.core.database import (
    get_db,
    init_db,
    close_db,
    engine,
    SessionLocal,
    Base,
)

__all__ = [
    "settings",
    "get_db",
    "init_db",
    "close_db",
    "engine",
    "SessionLocal",
    "Base",
]
