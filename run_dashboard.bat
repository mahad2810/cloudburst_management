@echo off
echo ======================================
echo  Cloudburst Management Dashboard
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/Update requirements
echo Installing required packages...
pip install -r requirements.txt --quiet
echo.

REM Run Streamlit app
echo Starting Streamlit Dashboard...
echo.
echo Dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
streamlit run app.py

pause
