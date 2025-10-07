"""
ff-storage: Database and file storage operations for Fenixflow applications.
"""

__version__ = "0.2.0"

from .db.migrations import MigrationManager
from .db.mysql import MySQL, MySQLPool

# Database exports
from .db.postgres import Postgres, PostgresPool

# Object storage exports
from .object import LocalObjectStorage, ObjectStorage, S3ObjectStorage

__all__ = [
    # PostgreSQL
    "Postgres",
    "PostgresPool",
    # MySQL
    "MySQL",
    "MySQLPool",
    # Migrations
    "MigrationManager",
    # Object Storage
    "ObjectStorage",
    "LocalObjectStorage",
    "S3ObjectStorage",
]
