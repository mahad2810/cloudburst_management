# 📚 Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Database Design](#database-design)
4. [Module Documentation](#module-documentation)
5. [API References](#api-references)
6. [Troubleshooting](#troubleshooting)

---

## Project Overview

### Purpose
The Cloudburst Management System is a comprehensive database-driven application designed to:
- Monitor and analyze rainfall patterns
- Track affected regions and risk levels
- Manage disaster relief resources
- Coordinate resource distribution
- Issue and manage alerts
- Provide AI-powered data insights

### Educational Objectives
This DBMS lab project demonstrates:
- **Database Design**: Proper normalization, relationships, and constraints
- **SQL Proficiency**: Complex queries, joins, aggregations, and stored procedures
- **Python-Database Integration**: Using mysql-connector and SQLAlchemy
- **Data Visualization**: Converting database queries into meaningful charts
- **Real-world Application**: Solving practical disaster management problems

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  (Multi-page Application with Interactive Dashboards)       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer (Python)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Connection   │  │  Query       │  │  Helper      │     │
│  │  Manager     │  │  Builder     │  │  Functions   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     MySQL Database                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  rainfall_   │  │  affected_   │  │  resources   │     │
│  │    data      │  │   regions    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │   alerts     │  │distribution_ │                       │
│  │              │  │     log      │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Services (Optional)               │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │   Mapbox     │  │   OpenAI     │                       │
│  │   (Maps)     │  │  (Chatbot)   │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack Layers

1. **Presentation Layer**: Streamlit (Web UI)
2. **Business Logic Layer**: Python (Data Processing)
3. **Data Access Layer**: MySQL Connector (Database Operations)
4. **Database Layer**: MySQL (Data Storage)
5. **Integration Layer**: External APIs (Mapbox, OpenAI)

---

## Database Design

### Entity-Relationship Diagram

```
┌─────────────────┐
│ rainfall_data   │
│─────────────────│
│ • id (PK)       │
│ • region        │
│ • date          │
│ • rainfall_mm   │
│ • temperature_c │
│ • humidity      │
└─────────────────┘

┌─────────────────────┐
│ affected_regions    │
│─────────────────────│
│ • region_id (PK)    │◄────┐
│ • region_name       │     │
│ • population        │     │
│ • risk_level        │     │
│ • warning_status    │     │
│ • last_update       │     │
│ • report_date       │     │
└─────────────────────┘     │
                            │
┌─────────────────────┐     │
│ alerts              │     │
│─────────────────────│     │
│ • alert_id (PK)     │     │
│ • region            │     │
│ • alert_message     │     │
│ • severity          │     │
│ • date_issued       │     │
│ • expiry_date       │     │
└─────────────────────┘     │
                            │
┌─────────────────────┐     │
│ resources           │     │
│─────────────────────│     │
│ • resource_id (PK)  │◄────┤
│ • resource_type     │     │
│ • quantity_available│     │
│ • location          │     │
│ • status            │     │
│ • last_restocked    │     │
└─────────────────────┘     │
        ▲                   │
        │                   │
        │                   │
┌───────┴──────────────┐    │
│ distribution_log     │    │
│──────────────────────│    │
│ • log_id (PK)        │    │
│ • region_id (FK)     ├────┘
│ • resource_id (FK)   │
│ • quantity_sent      │
│ • date_distributed   │
│ • received_date      │
│ • status             │
└──────────────────────┘
```

### Normalization Level: 3NF (Third Normal Form)

**1NF (First Normal Form):**
- All tables have atomic values
- Each column contains only one value
- No repeating groups

**2NF (Second Normal Form):**
- Meets 1NF requirements
- No partial dependencies
- All non-key attributes depend on entire primary key

**3NF (Third Normal Form):**
- Meets 2NF requirements
- No transitive dependencies
- Non-key attributes depend only on primary key

### Key Database Concepts Demonstrated

1. **Primary Keys**: Unique identifiers for each table
2. **Foreign Keys**: Maintaining referential integrity
3. **Indexes**: Optimizing query performance
4. **Constraints**: Data validation and integrity
5. **ENUM Types**: Predefined value sets
6. **Triggers**: Automated actions on data changes
7. **Stored Procedures**: Reusable database logic
8. **Views**: Simplified complex queries

---

## Module Documentation

### 1. `app.py` - Main Application
**Purpose**: Entry point for the Streamlit application

**Key Functions:**
- `main()`: Initialize and display landing page
- Page configuration and styling
- Navigation to multi-page sections

### 2. `config.py` - Configuration Management
**Purpose**: Centralized configuration settings

**Configuration Sections:**
- `DATABASE_CONFIG`: Database connection parameters
- `MAPBOX_TOKEN`: Map visualization API key
- `OPENAI_API_KEY`: AI chatbot integration
- `SEVERITY_COLORS`: UI color schemes

**Key Function:**
```python
def get_config(key: str, default: str = '') -> str:
    """
    Get configuration from Streamlit secrets or environment variables.
    Supports both local development and cloud deployment.
    """
```

### 3. `db/connection.py` - Database Connection Handler

**Class: `DatabaseConnection`**

**Methods:**
```python
def connect(host, database, user, password) -> bool:
    """Establish MySQL database connection"""

def disconnect() -> bool:
    """Close database connection"""

def execute_query(query: str, params=None) -> list:
    """Execute SELECT query and return results"""

def execute_update(query: str, params=None) -> bool:
    """Execute INSERT, UPDATE, DELETE queries"""

def fetch_dataframe(query: str) -> pd.DataFrame:
    """Execute query and return as pandas DataFrame"""
```

**Usage Example:**
```python
from db.connection import init_connection

db = init_connection()
results = db.execute_query("SELECT * FROM alerts WHERE severity = 'Critical'")
```

### 4. `db/queries.py` - SQL Query Helper

**Class: `QueryHelper`**

**Categories:**
- Rainfall Data Queries
- Affected Regions Queries
- Resources Queries
- Alerts Queries
- Distribution Log Queries

**Example Methods:**
```python
@staticmethod
def get_all_rainfall_data():
    """Get all rainfall records"""
    return "SELECT * FROM rainfall_data ORDER BY date DESC"

@staticmethod
def get_high_risk_regions():
    """Get regions with high or critical risk"""
    return """
        SELECT region_id, region_name, population, risk_level
        FROM affected_regions
        WHERE risk_level IN ('High', 'Critical')
        ORDER BY risk_level DESC
    """
```

### 5. `db/mapbox_helper.py` - Map Visualization

**Purpose**: Generate interactive maps with Mapbox

**Key Functions:**
```python
def create_rainfall_map(data: pd.DataFrame) -> str:
    """Create HTML map visualization for rainfall data"""

def add_region_markers(map_obj, regions: list):
    """Add markers for affected regions"""
```

### 6. `db/openai_helper.py` - AI Integration

**Purpose**: OpenAI GPT integration for chatbot

**Key Functions:**
```python
def generate_response(prompt: str, context: dict) -> str:
    """Generate AI response based on database context"""

def create_context_from_data(data: pd.DataFrame) -> str:
    """Convert database results to context for AI"""
```

### 7. `db/rag_helper.py` - Retrieval Augmented Generation

**Purpose**: Enhanced AI responses with database context

**Key Functions:**
```python
def retrieve_relevant_data(query: str, db) -> dict:
    """Retrieve relevant database records for user query"""

def generate_augmented_response(query: str, data: dict) -> str:
    """Generate AI response augmented with database data"""
```

---

## API References

### Database Query Examples

#### 1. Complex JOIN Query
```sql
-- Get distribution statistics with resource and region details
SELECT 
    ar.region_name,
    r.resource_type,
    SUM(dl.quantity_sent) as total_distributed,
    COUNT(dl.log_id) as distribution_count,
    AVG(DATEDIFF(dl.received_date, dl.date_distributed)) as avg_delivery_days
FROM distribution_log dl
INNER JOIN affected_regions ar ON dl.region_id = ar.region_id
INNER JOIN resources r ON dl.resource_id = r.resource_id
WHERE dl.status = 'Delivered'
GROUP BY ar.region_name, r.resource_type
ORDER BY total_distributed DESC;
```

#### 2. Aggregation with Window Functions
```sql
-- Calculate rainfall trends with moving averages
SELECT 
    region,
    date,
    rainfall_mm,
    AVG(rainfall_mm) OVER (
        PARTITION BY region 
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day
FROM rainfall_data
ORDER BY region, date DESC;
```

#### 3. Subquery Example
```sql
-- Find regions with above-average rainfall
SELECT 
    region,
    AVG(rainfall_mm) as avg_rainfall
FROM rainfall_data
GROUP BY region
HAVING avg_rainfall > (
    SELECT AVG(rainfall_mm) FROM rainfall_data
)
ORDER BY avg_rainfall DESC;
```

### Python API Examples

#### Database Connection
```python
from db.connection import DatabaseConnection

# Initialize connection
db = DatabaseConnection()
db.connect(host='localhost', database='cloudburst_management', 
           user='root', password='password')

# Execute query
results = db.execute_query("SELECT * FROM alerts WHERE severity = 'Critical'")

# Get as DataFrame
df = db.fetch_dataframe("SELECT * FROM rainfall_data")

# Close connection
db.disconnect()
```

#### Using Query Helper
```python
from db.queries import QueryHelper
from db.connection import init_connection

db = init_connection()

# Get pre-defined query
query = QueryHelper.get_active_alerts()
alerts_df = db.fetch_dataframe(query)

# Get rainfall by region
query = QueryHelper.get_rainfall_by_region('Uttarakhand')
data = db.execute_query(query)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Failed
**Error**: `mysql.connector.errors.DatabaseError: Access denied`

**Solutions:**
- Check MySQL service is running
- Verify credentials in `.env` file
- Ensure database exists: `CREATE DATABASE cloudburst_management;`
- Check MySQL user permissions: `GRANT ALL ON cloudburst_management.* TO 'user'@'localhost';`

#### 2. Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solutions:**
- Activate virtual environment: `venv\Scripts\activate`
- Install requirements: `pip install -r requirements.txt`
- Verify Python version: `python --version` (3.11+ required)

#### 3. Mapbox Not Displaying
**Error**: Map shows grey box or error

**Solutions:**
- Check `MAPBOX_TOKEN` in `.env`
- Verify token is valid at mapbox.com
- Check internet connection
- Try fallback map (Folium instead of PyDeck)

#### 4. OpenAI Chatbot Not Working
**Error**: `openai.error.AuthenticationError`

**Solutions:**
- Verify `OPENAI_API_KEY` in `.env`
- Check API key is active at platform.openai.com
- Verify account has credits/billing setup
- Check API rate limits

#### 5. Data Not Loading
**Error**: Empty tables or no data displayed

**Solutions:**
- Import sample data from CSV files
- Run: `LOAD DATA INFILE 'file.csv' INTO TABLE table_name;`
- Check table exists: `SHOW TABLES;`
- Verify data: `SELECT COUNT(*) FROM table_name;`

### Performance Optimization Tips

1. **Add Indexes**: For frequently queried columns
```sql
CREATE INDEX idx_region_date ON rainfall_data(region, date);
```

2. **Use Query Caching**: For repeated queries
```python
@st.cache_data(ttl=300)
def get_rainfall_data():
    return db.fetch_dataframe("SELECT * FROM rainfall_data")
```

3. **Limit Result Sets**: Use LIMIT for large tables
```sql
SELECT * FROM rainfall_data ORDER BY date DESC LIMIT 100;
```

4. **Optimize Joins**: Use appropriate JOIN types
```sql
-- Use INNER JOIN when possible (faster than LEFT JOIN)
SELECT * FROM alerts a
INNER JOIN affected_regions ar ON a.region = ar.region_name;
```

---

## Additional Resources

### Learning Materials
- **MySQL Documentation**: https://dev.mysql.com/doc/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Pandas Guide**: https://pandas.pydata.org/docs/
- **Plotly Charts**: https://plotly.com/python/

### Related Topics
- Database Normalization
- SQL Query Optimization
- Data Visualization Best Practices
- Python-Database Integration
- RESTful API Design

---

**Last Updated**: November 2024  
**Version**: 1.0  
**Maintainer**: Mahad (@mahad2810)
