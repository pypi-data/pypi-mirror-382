"""
WowMySQL Python SDK
Official client library for WowMySQL REST API v2
"""

from .client import WowMySQLClient, WowMySQLError
from .table import Table, QueryBuilder
from .types import (
    QueryOptions,
    FilterExpression,
    QueryResponse,
    CreateResponse,
    UpdateResponse,
    DeleteResponse,
    TableSchema,
    ColumnInfo,
)

__version__ = "0.1.3"
__all__ = [
    "WowMySQLClient",
    "WowMySQLError",
    "Table",
    "QueryBuilder",
    "QueryOptions",
    "FilterExpression",
    "QueryResponse",
    "CreateResponse",
    "UpdateResponse",
    "DeleteResponse",
    "TableSchema",
    "ColumnInfo",
]

