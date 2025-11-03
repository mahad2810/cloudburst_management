"""
Database Package
Handles MySQL database connections and queries for Cloudburst Management System
"""

from .connection import DatabaseConnection, get_database_connection, init_connection
from .queries import QueryHelper

__all__ = [
    'DatabaseConnection',
    'get_database_connection',
    'init_connection',
    'QueryHelper'
]

__version__ = '1.0.0'
__author__ = 'Mahad Iqbal'
