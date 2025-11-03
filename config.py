"""
Configuration file for Streamlit Dashboard
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration (Load from .env with fallback defaults)
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_DATABASE', 'cloudburst_management'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Map Configuration
MAP_CENTER = [20.5937, 78.9629]  # India center
MAP_ZOOM = 5

# Mapbox Configuration (Load from .env)
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN', '')
MAPBOX_STYLE = "mapbox://styles/mapbox/dark-v11"

# OpenAI Configuration (Load from .env)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
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
