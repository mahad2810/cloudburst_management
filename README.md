# 🌧️ Cloudburst Management System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MySQL](https://img.shields.io/badge/mysql-8.0%2B-orange.svg)](https://www.mysql.com/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A comprehensive Database Management System (DBMS) project for monitoring, analyzing, and responding to cloudburst incidents and natural disaster management.

> 🎓 **Academic Project**: Developed as part of DBMS Lab coursework to demonstrate practical database application development, SQL proficiency, and data visualization techniques.

## 📋 Project Overview

The Cloudburst Management System is an interactive web-based dashboard built with **Streamlit** and **MySQL** that provides real-time monitoring, analytics, and AI-powered assistance for disaster management. This project demonstrates advanced database concepts including query optimization, data visualization, and integration with modern APIs.

### 🎓 Academic Project
This project was developed as part of the **Database Management Systems (DBMS) Lab** course at college, showcasing practical implementation of database concepts including:
- Database design and normalization
- Complex SQL queries and joins
- Data analytics and aggregation
- Database connectivity with Python
- Real-time data visualization
- AI/ML integration with databases

## ✨ Key Features

### 1. 🏠 Home Dashboard
- **Real-time KPIs**: Monitor active alerts, resources, and affected regions
- **Risk Prediction**: ML-based cloudburst risk assessment
- **Interactive Charts**: Rainfall trends, resource distribution, and severity analysis
- **Recent Activity Feed**: Latest alerts and distribution logs

### 2. 📊 Rainfall Analytics
- **Comprehensive Data Analysis**: View rainfall data by region and time period
- **Interactive Maps**: Mapbox-powered geographical visualization
- **Statistical Insights**: Average, maximum, and trend analysis
- **Time-series Graphs**: Historical rainfall patterns with Plotly

### 3. 📦 Resource Overview
- **Inventory Management**: Track resources across multiple locations
- **Stock Monitoring**: Low-stock alerts and availability status
- **Resource Allocation**: View distribution by type and location
- **Visual Analytics**: Interactive charts for resource planning

### 4. 🚨 Alert Center
- **Active Alerts Dashboard**: Real-time disaster alerts by severity
- **Severity Classification**: Critical, High, Medium, Low priority levels
- **Expiry Tracking**: Monitor alert validity periods
- **Regional Breakdown**: Alerts organized by affected regions

### 5. 📋 Distribution Log
- **Delivery Tracking**: Monitor resource distribution to affected areas
- **Timeline Visualization**: Distribution history and patterns
- **Status Monitoring**: Track pending, in-transit, and completed deliveries
- **Analytics**: Distribution efficiency and resource utilization

### 6. 🗄️ Database Explorer
- **Interactive SQL Console**: Execute custom queries directly
- **Table Browser**: Explore all database tables
- **Data Export**: Download query results as CSV
- **Query History**: Track and reuse previous queries

### 7. 🤖 AI Chatbot Assistant
- **Natural Language Queries**: Ask questions about data in plain English
- **OpenAI Integration**: Powered by GPT-4 for intelligent responses
- **Context-Aware**: Understands database schema and relationships
- **Data Visualization**: Auto-generates charts based on queries
- **CSV Support**: Query data directly from CSV files

## 🛠️ Technology Stack

### Backend & Database
- **Python 3.11+**: Core programming language
- **MySQL**: Relational database management system
- **SQLAlchemy**: Database ORM and toolkit
- **mysql-connector-python**: MySQL database driver

### Frontend & Visualization
- **Streamlit**: Web application framework
- **Plotly**: Interactive charts and graphs
- **Folium**: Map visualizations
- **PyDeck**: Advanced 3D map rendering
- **Altair**: Declarative statistical visualization

### AI & APIs
- **OpenAI GPT-4**: Natural language processing for chatbot
- **Mapbox**: Advanced mapping and geospatial analysis

### Development Tools
- **python-dotenv**: Environment variable management
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

## 📁 Project Structure

```
cloudburst_management/
│
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Configuration and environment variables
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation (this file)
├── LICENSE                     # MIT License
├── DEPLOYMENT.md              # Deployment guide for Streamlit Cloud
├── .env.example               # Sample environment variables
├── .gitignore                 # Git ignore rules
│
├── db/                        # Database modules
│   ├── __init__.py           # Package initializer
│   ├── connection.py         # Database connection handler
│   ├── queries.py            # Pre-defined SQL queries
│   ├── mapbox_helper.py      # Mapbox integration utilities
│   ├── openai_helper.py      # OpenAI API integration
│   ├── rag_helper.py         # RAG (Retrieval Augmented Generation)
│   └── region_polygons.py    # Geographical region definitions
│
├── pages/                     # Streamlit multi-page application
│   ├── 1_Home_Dashboard.py   # Main dashboard with KPIs
│   ├── 2_Rainfall_Analytics.py   # Rainfall data analysis
│   ├── 3_Resource_Overview.py    # Resource inventory management
│   ├── 4_Alert_Center.py         # Alert monitoring system
│   ├── 5_Distribution_Log.py     # Distribution tracking
│   ├── 6_Database_Explorer.py    # SQL query interface
│   └── 7_Chatbot_Assistant.py    # AI-powered assistant
│
├── csv_sheets/                # Sample CSV data files
│   ├── rainfall_data.csv
│   ├── affected_regions.csv
│   ├── alerts.csv
│   ├── resources.csv
│   └── distribution_log.csv
│
├── assets/                    # Static assets (images, icons)
│
└── .streamlit/               # Streamlit configuration
    ├── config.toml           # App configuration
    └── secrets.toml          # API keys (not in git)
```

## 🗃️ Database Schema

The system uses a MySQL database with the following tables:

### 1. `rainfall_data`
Stores historical rainfall measurements and weather data.

```sql
CREATE TABLE rainfall_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    region VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    rainfall_mm DECIMAL(10, 2),
    temperature_c DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    INDEX idx_region (region),
    INDEX idx_date (date)
);
```

### 2. `affected_regions`
Tracks regions affected by cloudbursts with risk assessments.

```sql
CREATE TABLE affected_regions (
    region_id INT PRIMARY KEY AUTO_INCREMENT,
    region_name VARCHAR(100) NOT NULL UNIQUE,
    population INT,
    risk_level ENUM('Low', 'Medium', 'High', 'Critical'),
    warning_status BOOLEAN DEFAULT FALSE,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_date DATE,
    INDEX idx_risk_level (risk_level)
);
```

### 3. `alerts`
Manages disaster alerts and warnings.

```sql
CREATE TABLE alerts (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    region VARCHAR(100) NOT NULL,
    alert_message TEXT NOT NULL,
    severity ENUM('Low', 'Medium', 'High', 'Critical'),
    date_issued DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME,
    INDEX idx_severity (severity),
    INDEX idx_region (region)
);
```

### 4. `resources`
Inventory management for disaster relief resources.

```sql
CREATE TABLE resources (
    resource_id INT PRIMARY KEY AUTO_INCREMENT,
    resource_type VARCHAR(100) NOT NULL,
    quantity_available INT NOT NULL,
    location VARCHAR(100),
    status ENUM('Available', 'Low Stock', 'Depleted') DEFAULT 'Available',
    last_restocked DATE,
    INDEX idx_location (location),
    INDEX idx_status (status)
);
```

### 5. `distribution_log`
Tracks resource distribution to affected areas.

```sql
CREATE TABLE distribution_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    region_id INT,
    resource_id INT,
    quantity_sent INT NOT NULL,
    date_distributed DATE NOT NULL,
    received_date DATE,
    status ENUM('Pending', 'In Transit', 'Delivered') DEFAULT 'Pending',
    FOREIGN KEY (region_id) REFERENCES affected_regions(region_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    INDEX idx_status (status),
    INDEX idx_date (date_distributed)
);
```

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.11 or higher**
- **MySQL 8.0 or higher**
- **Git** (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/mahad2810/cloudburst_management.git
cd cloudburst_management
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

1. **Create MySQL Database**:
```sql
CREATE DATABASE cloudburst_management;
USE cloudburst_management;
```

2. **Import Schema**: Run the SQL commands from the `Database Schema` section above, or use the provided SQL file:
```bash
mysql -u root -p cloudburst_management < database_schema.sql
```

3. **Load Sample Data** (optional):
```bash
# Import CSV data using MySQL LOAD DATA or the application's import feature
```

### Step 5: Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
# Database Configuration
DB_HOST=localhost
DB_DATABASE=cloudburst_management
DB_USER=root
DB_PASSWORD=your_password
DB_PORT=3306

# Mapbox API (Optional - for map features)
MAPBOX_TOKEN=your_mapbox_token_here

# OpenAI API (Optional - for chatbot)
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 6: Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 🔧 Configuration

### Database Connection
Edit `config.py` to customize database settings:
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'cloudburst_management',
    'user': 'root',
    'password': 'your_password',
    'port': 3306
}
```

### API Keys (Optional Features)

#### Mapbox Token (for advanced maps)
1. Sign up at [mapbox.com](https://www.mapbox.com/)
2. Create an access token
3. Add to `.env`: `MAPBOX_TOKEN=your_token`

#### OpenAI API Key (for AI chatbot)
1. Sign up at [platform.openai.com](https://platform.openai.com/)
2. Create an API key
3. Add to `.env`: `OPENAI_API_KEY=your_key`

## 📊 Usage Examples

### Running SQL Queries
Navigate to **Database Explorer** page:
```sql
-- Get regions with highest rainfall
SELECT region, SUM(rainfall_mm) as total_rainfall
FROM rainfall_data
GROUP BY region
ORDER BY total_rainfall DESC
LIMIT 10;
```

### Using the Chatbot
Navigate to **Chatbot Assistant** page and ask:
- "Show me regions with critical alerts"
- "What is the total available resources?"
- "Which regions received the most distributions?"

## 🎯 Key Database Concepts Demonstrated

1. **Normalization**: Tables follow 3NF principles
2. **Indexing**: Strategic indexes on frequently queried columns
3. **Foreign Keys**: Maintaining referential integrity
4. **Aggregation**: Complex GROUP BY and aggregate functions
5. **Joins**: Multi-table queries with INNER/LEFT joins
6. **Transactions**: ACID compliance for data integrity
7. **Query Optimization**: Efficient query design and execution
8. **Data Visualization**: Converting raw data into insights

## 🤝 Contributing

This is an academic project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Mahad** - [@mahad2810](https://github.com/mahad2810)

## 🙏 Acknowledgments

- College DBMS Lab Course Instructors
- Streamlit Community for excellent documentation
- OpenAI for GPT-4 API
- Mapbox for geospatial visualization tools
- MySQL Documentation and Community

## � Additional Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 10 minutes
- **[Technical Documentation](DOCUMENTATION.md)** - In-depth technical details
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Database Schema](database_schema.sql)** - Complete SQL schema

## �📧 Contact

For questions or support:
- 📫 Open an issue on [GitHub Issues](https://github.com/mahad2810/cloudburst_management/issues)
- 💬 Start a [Discussion](https://github.com/mahad2810/cloudburst_management/discussions)
- 👤 Contact via [GitHub Profile](https://github.com/mahad2810)

## 📊 Project Statistics

- **Lines of Code**: 5000+
- **Database Tables**: 5
- **Dashboard Pages**: 7
- **SQL Queries**: 50+
- **Python Modules**: 15+

---

<div align="center">

**⭐ If you find this project helpful, please consider giving it a star! ⭐**

*Developed as part of DBMS Lab Project*  
*Demonstrating practical database application development*

[![GitHub stars](https://img.shields.io/github/stars/mahad2810/cloudburst_management?style=social)](https://github.com/mahad2810/cloudburst_management/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mahad2810/cloudburst_management?style=social)](https://github.com/mahad2810/cloudburst_management/network/members)

</div>
