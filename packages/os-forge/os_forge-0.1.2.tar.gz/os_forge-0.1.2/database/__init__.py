"""
Database module for OS Forge
Contains SQLAlchemy models and database management
"""

from .models import HardeningResult, Base
from .manager import DatabaseManager, get_db, init_db

__all__ = ['HardeningResult', 'Base', 'DatabaseManager', 'get_db', 'init_db']

