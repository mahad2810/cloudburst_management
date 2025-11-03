"""
Database Connection Module
Handles MySQL connection setup and management
"""

import mysql.connector
from mysql.connector import Error
import streamlit as st
from typing import Optional
import pandas as pd


class DatabaseConnection:
    """Manages MySQL database connections for the Cloudburst Management System"""
    
    def __init__(self):
        """Initialize database connection parameters"""
        self.connection = None
        self.cursor = None
    
    def connect(self, host: str = "localhost", 
                database: str = "cloudburst_management",
                user: str = "root", 
                password: str = "") -> bool:
        """
        Establish connection to MySQL database
        
        Args:
            host: Database host address
            database: Database name
            user: Database username
            password: Database password
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                return True
            return False
            
        except Error as e:
            st.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection safely"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Error as e:
            st.error(f"Error closing connection: {e}")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """
        Execute SELECT query and return results
        
        Args:
            query: SQL SELECT statement
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries containing query results
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            return results
            
        except Error as e:
            st.error(f"Query execution error: {e}")
            return None
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """
        Execute INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL statement
            params: Query parameters (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return True
            
        except Error as e:
            st.error(f"Update execution error: {e}")
            self.connection.rollback()
            return False
    
    def fetch_dataframe(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Execute query and return results as pandas DataFrame
        
        Args:
            query: SQL SELECT statement
            params: Query parameters (optional)
            
        Returns:
            pandas DataFrame containing query results
        """
        try:
            if params:
                df = pd.read_sql(query, self.connection, params=params)
            else:
                df = pd.read_sql(query, self.connection)
            return df
            
        except Error as e:
            st.error(f"DataFrame fetch error: {e}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name: str) -> Optional[list]:
        """
        Get column information for a specific table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column definitions
        """
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)


# Singleton instance for reuse across pages
@st.cache_resource
def get_database_connection():
    """
    Get or create database connection instance
    Uses Streamlit caching to maintain single connection
    """
    db = DatabaseConnection()
    return db


def init_connection(host: str = "localhost",
                   database: str = "cloudburst_management", 
                   user: str = "root",
                   password: str = "") -> DatabaseConnection:
    """
    Initialize database connection with credentials
    
    Args:
        host: Database host
        database: Database name
        user: Database username
        password: Database password
        
    Returns:
        DatabaseConnection instance
    """
    db = get_database_connection()
    if not db.connection or not db.connection.is_connected():
        success = db.connect(host, database, user, password)
        if not success:
            st.error("Failed to connect to database. Please check credentials.")
    return db
