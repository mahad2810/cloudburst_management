"""
Configuration file for Streamlit Dashboard
Supports both local .env files and Streamlit Cloud secrets
"""
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file (for local development)
load_dotenv()

# Helper function to get config values from Streamlit secrets or environment variables
def get_config(key: str, default: str = ''):
    """Get configuration from Streamlit secrets (if deployed) or environment variables (if local)"""
    try:
        # Try Streamlit secrets first (for deployment)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    # Fallback to environment variables (for local development)
    return os.getenv(key, default)

# Database Configuration
DATABASE_CONFIG = {
    'host': get_config('DB_HOST', 'localhost'),
    'database': get_config('DB_DATABASE', 'cloudburst_management'),
    'user': get_config('DB_USER', 'root'),
    'password': get_config('DB_PASSWORD', ''),
    'port': int(get_config('DB_PORT', '3306'))
}

# Map Configuration
MAP_CENTER = [20.5937, 78.9629]  # India center
MAP_ZOOM = 5

# Mapbox Configuration
MAPBOX_TOKEN = get_config('MAPBOX_TOKEN', '')
MAPBOX_STYLE = "mapbox://styles/mapbox/dark-v11"

# OpenAI Configuration
OPENAI_API_KEY = get_config('OPENAI_API_KEY', '')
OPENAI_MODEL = "gpt-4-turbo-preview"  # or "gpt-3.5-turbo" for faster/cheaper
OPENAI_TEMPERATURE = 0.3  # Lower = more focused responses
OPENAI_MAX_TOKENS = 1000

# Color Schemes
SEVERITY_COLORS = {
    'Critical': '#FF1744',
    'High': '#FF6F00',
    'Moderate': '#FDD835',
    'Low': '#4CAF50'
}

STATUS_COLORS = {
    'Available': '#4CAF50',
    'In Use': '#FDD835',
    'Depleted': '#FF1744'
}

# Thresholds
LOW_STOCK_THRESHOLD = 100
CRITICAL_STOCK_THRESHOLD = 50

# Pagination
DEFAULT_PAGE_SIZE = 100
MAX_RECORDS_DISPLAY = 1000

# Chart Configuration
CHART_TEMPLATE = 'plotly_dark'
CHART_HEIGHT = 400

# Date Formats
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# File Export
EXPORT_DATE_FORMAT = '%Y%m%d_%H%M%S'

# Session Configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Feature Flags
ENABLE_AI_CHATBOT = True
ENABLE_EXPORT = True
ENABLE_DELETE = True
ENABLE_MAPS = True
