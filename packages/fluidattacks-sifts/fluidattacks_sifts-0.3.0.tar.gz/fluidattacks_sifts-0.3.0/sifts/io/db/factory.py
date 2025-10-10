"""Factory for creating database backends."""

import os
from enum import Enum
from typing import Any

from sifts.io.db.base import DatabaseBackend
from sifts.io.db.dynamodb_backend import DynamoDBBackend
from sifts.io.db.sqlite_backend import SQLiteBackend


class DatabaseBackendType(Enum):
    """Available database backend types."""

    DYNAMODB = "dynamodb"
    SQLITE = "sqlite"


def create_database_backend(
    backend_type: str | DatabaseBackendType | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> DatabaseBackend:
    """
    Create a database backend instance.

    Args:
        backend_type: The type of backend to create. If None, will check
                     SIFTS_DB_BACKEND environment variable, defaulting to 'dynamodb'.
        **kwargs: Additional arguments passed to the backend constructor.

    Returns:
        DatabaseBackend: An instance of the requested backend.

    Raises:
        ValueError: If the backend type is not supported.

    """
    if backend_type is None:
        backend_type = os.getenv("SIFTS_DB_BACKEND", "dynamodb")

    if isinstance(backend_type, str):
        backend_type = backend_type.lower()

    if backend_type in {DatabaseBackendType.DYNAMODB, "dynamodb"}:
        return DynamoDBBackend()

    if backend_type in {DatabaseBackendType.SQLITE, "sqlite"}:
        # Extract SQLite-specific kwargs
        sqlite_kwargs = {
            "database_path": kwargs.get("database_path", "sifts.db"),
        }
        return SQLiteBackend(**sqlite_kwargs)
    msg = f"Unsupported database backend type: {backend_type}"
    raise ValueError(msg)
