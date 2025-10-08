
"""
This module serves as the main entry point for the SQLMorph library.
It re-exports the core components of SQLModel, allowing developers to use
SQLMorph as a drop-in replacement for SQLModel while gaining migration
capabilities.
"""

from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    create_engine,
    Session,
    select
)

# This makes it so `from sqlmorph import SQLModel` works just like `from sqlmodel import SQLModel`.
# We will add our custom logic and hooks to this module later.

__all__ = [
    "SQLModel",
    "Field",
    "Relationship",
    "create_engine",
    "Session",
    "select",
]

print("SQLMorph core module initialized. Ready to be imported.")

