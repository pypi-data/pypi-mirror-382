
"""
SQLMorph: SQLModel with Built-in Migrations.

This is the main entry point for users of the library.
"""

# Re-export the core components from SQLModel via our core module
from .core import (
    SQLModel,
    Field,
    Relationship,
    create_engine,
    Session,
    select
)

__all__ = [
    "SQLModel",
    "Field",
    "Relationship",
    "create_engine",
    "Session",
    "select",
]
