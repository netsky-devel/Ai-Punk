"""
Database layer for Smart Context Manager
SurrealDB connection, schema, and queries
"""

from .connection import SurrealConnection
from .schema import setup_context_schema
from .queries import ContextQueries

__all__ = ['SurrealConnection', 'setup_context_schema', 'ContextQueries'] 