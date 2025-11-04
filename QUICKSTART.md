# 🚀 Quick Start Guide

Get the Cloudburst Management System running in under 10 minutes!

## Prerequisites Checklist

Before you begin, ensure you have:
- [ ] **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- [ ] **MySQL 8.0+** installed ([Download](https://dev.mysql.com/downloads/))
- [ ] **Git** installed ([Download](https://git-scm.com/downloads))
- [ ] Basic knowledge of terminal/command prompt

## Step-by-Step Installation

### 1️⃣ Clone the Repository (2 minutes)

```bash
# Open your terminal/command prompt
git clone https://github.com/mahad2810/cloudburst_management.git
cd cloudburst_management
```

### 2️⃣ Set Up Virtual Environment (2 minutes)

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3️⃣ Install Dependencies (3 minutes)

```bash
pip install -r requirements.txt
```

Wait for all packages to install...

### 4️⃣ Set Up MySQL Database (3 minutes)

**Option A: Using MySQL Command Line**
```sql
-- Login to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE cloudburst_management;
USE cloudburst_management;

-- Import schema
SOURCE database_schema.sql;

-- Verify tables
SHOW TABLES;
```

**Option B: Using MySQL Workbench**
1. Open MySQL Workbench
2. Create new connection to localhost
3. Create new schema: `cloudburst_management`
4. File → Run SQL Script → Select `database_schema.sql`
5. Execute

### 5️⃣ Configure Environment (1 minute)

**Windows:**
```powershell
Copy-Item .env.example .env
notepad .env
```

**macOS/Linux:**
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Edit the `.env` file:**
```env
DB_HOST=localhost
DB_DATABASE=cloudburst_management
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD  # ← Change this!
DB_PORT=3306

# Optional (can add later)
MAPBOX_TOKEN=
OPENAI_API_KEY=
```

**Save and close the file.**

### 6️⃣ Run the Application (30 seconds)

**Windows:**
```powershell
streamlit run app.py
```

**Or use the batch file:**
```powershell
.\run_dashboard.bat
```

**macOS/Linux:**
```bash
streamlit run app.py
```

The app will automatically open in your browser at: `http://localhost:8501`

## 🎉 Success!

You should now see the Cloudburst Management System dashboard!

### First Steps After Installation

1. **Explore the Dashboard** - Check out all 7 pages in the sidebar
2. **View Sample Data** - Navigate to Database Explorer
3. **Test Features** - Try different analytics and visualizations

### Optional: Enable Advanced Features

#### 🗺️ Enable Map Visualizations

1. Go to [mapbox.com](https://account.mapbox.com/access-tokens/)
2. Sign up for free account
3. Copy your access token
4. Add to `.env`: `MAPBOX_TOKEN=pk.your_token_here`
5. Restart the app

#### 🤖 Enable AI Chatbot

1. Go to [platform.openai.com](https://platform.openai.com/api-keys)
2. Create account and API key
3. Add to `.env`: `OPENAI_API_KEY=sk-your_key_here`
4. Restart the app
5. Navigate to Chatbot Assistant page

## 🐛 Troubleshooting

### Database Connection Failed?
```bash
# Test MySQL connection
mysql -u root -p -e "SHOW DATABASES;"

# Verify credentials in .env match MySQL user
```

### Port Already in Use?
```bash
# Kill process on port 8501 (Windows)
netstat -ano | findstr :8501
taskkill /PID <process_id> /F

# Or use different port
streamlit run app.py --server.port 8502
```

### Module Not Found Error?
```bash
# Ensure virtual environment is activated
# Should see (venv) in terminal

# Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Import CSV Data
```sql
-- If tables are empty, you can import CSV files
LOAD DATA LOCAL INFILE 'csv_sheets/rainfall_data.csv'
INTO TABLE rainfall_data
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

## 📚 Next Steps

1. **Read the README.md** - Comprehensive project documentation
2. **Explore DOCUMENTATION.md** - Technical details and API reference
3. **Check DEPLOYMENT.md** - Deploy to Streamlit Cloud
4. **Read CONTRIBUTING.md** - Learn how to contribute

## 🆘 Need Help?

- **Documentation Issues**: Check DOCUMENTATION.md
- **Database Questions**: Review database_schema.sql
- **Feature Requests**: Open a GitHub issue
- **General Help**: Create a discussion on GitHub

## 🎯 Quick Command Reference

```bash
# Activate virtual environment
venv\Scripts\activate              # Windows
source venv/bin/activate           # macOS/Linux

# Run application
streamlit run app.py

# Run on different port
streamlit run app.py --server.port 8502

# Deactivate virtual environment
deactivate

# Update dependencies
pip install --upgrade -r requirements.txt

# Database backup
mysqldump -u root -p cloudburst_management > backup.sql

# Database restore
mysql -u root -p cloudburst_management < backup.sql
```

## 📊 Test Your Setup

Visit these URLs after starting the app:
- Home: http://localhost:8501
- Database Explorer: http://localhost:8501/Database_Explorer
- Chatbot: http://localhost:8501/Chatbot_Assistant

Run this test query in Database Explorer:
```sql
SELECT COUNT(*) as table_count FROM information_schema.tables 
WHERE table_schema = 'cloudburst_management';
```

Should return: **5 tables**

---

**Congratulations! 🎊 You're all set up!**

If everything is working, please ⭐ star the repository on GitHub!

---

**Installation Time**: ~10 minutes  
**Difficulty**: Beginner-Friendly  
**Support**: Open an issue on GitHub
