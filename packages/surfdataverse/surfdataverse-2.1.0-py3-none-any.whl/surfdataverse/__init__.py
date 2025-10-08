"""
SurfDataverse - A Python package for Microsoft Dataverse integration

This package provides a clean, object-oriented interface for connecting to,
reading from, and writing to Microsoft Dataverse environments.

Main Components:
- DataverseClient: Authentication and connection management
- DataverseRow: Base class for entity operations
- Entity classes: Article, Recipe, Ingredient, etc.
"""

from .core import DataverseClient, DataverseTable, is_valid_guid
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    DataverseAPIError,
    EntityError,
    SurfDataverseError,
    ValidationError,
)

__author__ = "Friedemann Heinz"

__all__ = [
    "DataverseClient",
    "DataverseTable",
    "is_valid_guid",
    "SurfDataverseError",
    "AuthenticationError",
    "ConnectionError",
    "ConfigurationError",
    "DataverseAPIError",
    "EntityError",
    "ValidationError",
]
