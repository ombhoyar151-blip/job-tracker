"""Cross-database type compatibility layer.

Provides UUID and JSONB types that work with both PostgreSQL and SQLite.
"""

import uuid as _uuid

from sqlalchemy import TypeDecorator, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB


def _is_sqlite(dialect_name: str) -> bool:
    return dialect_name == "sqlite"


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's native UUID type when available, otherwise stores as string.
    """

    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return str(value) if isinstance(value, _uuid.UUID) else value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return _uuid.UUID(value) if isinstance(value, str) else value


class JSONB(TypeDecorator):
    """Platform-independent JSONB type.

    Uses PostgreSQL's native JSONB when available, otherwise stores as text.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        import json
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        import json
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
