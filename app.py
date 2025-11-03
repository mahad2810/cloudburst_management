"""
🌧️ Cloudburst Management System - Main Dashboard
Smart Visualization, Analytics & Management Interface
"""

import streamlit as st
from db.connection import init_connection
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="Cloudburst Management System",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Cloudburst Management System\n\nA comprehensive disaster management platform for monitoring and responding to cloudburst incidents."
    }
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    h1 {
        color: #4FC3F7;
        font-weight: 700;
    }
    h2, h3 {
        color: #81D4FA;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric:hover {
        box-shadow: 0 6px 12px rgba(79, 195, 247, 0.3);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    .sidebar .sidebar-content {
        background-color: #1e2130;
    }
    .stButton>button {
        background-color: #4FC3F7;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0288D1;
        box-shadow: 0 4px 12px rgba(79, 195, 247, 0.4);
    }
    .info-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .warning-box {
        background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: white;
        font-weight: 600;
    }
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for database connection
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
    # Load credentials from config
    import config
    st.session_state.db_config = config.DATABASE_CONFIG.copy()

def show_sidebar():
    """Display sidebar with navigation and database configuration"""
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/rain.png", width=100)
        st.title("🌧️ Cloudburst MS")
        st.markdown("---")
        
        # Connection Status
        if st.session_state.db_connected:
            st.success(f"✅ Connected to: **{st.session_state.db_config['database']}**")
            with st.expander("⚙️ Database Info"):
                st.info(f"""
                **Host:** {st.session_state.db_config['host']}  
                **Database:** {st.session_state.db_config['database']}  
                **User:** {st.session_state.db_config['user']}
                """)
                if st.button("🔄 Reconnect", use_container_width=True):
                    connect_to_database()
        else:
            st.error("❌ Database Connection Failed")
            with st.expander("⚙️ Database Configuration", expanded=True):
                st.text_input("Host", value=st.session_state.db_config['host'], 
                             key='db_host', on_change=update_db_config)
                st.text_input("Database", value=st.session_state.db_config['database'], 
                             key='db_database', on_change=update_db_config)
                st.text_input("User", value=st.session_state.db_config['user'], 
                             key='db_user', on_change=update_db_config)
                st.text_input("Password", value=st.session_state.db_config['password'], 
                             type='password', key='db_password', on_change=update_db_config)
                
                if st.button("🔌 Connect to Database", use_container_width=True):
                    connect_to_database()
        
        st.markdown("---")
        
        # Navigation Info
        st.markdown("### 📍 Navigation")
        st.markdown("""
        Use the sidebar to navigate between:
        - 🏠 **Home Dashboard** - Overview & KPIs
        - 📊 **Rainfall Analytics** - Data insights
        - 📦 **Resource Overview** - Inventory management
        - ⚠️ **Alert Center** - Warning system
        - 🚚 **Distribution Log** - Aid tracking
        - 💾 **Database Explorer** - Direct data access
        - 🤖 **Chatbot Assistant** - AI helper
        """)
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.info("""
        **Cloudburst Management System**
        
        A comprehensive platform for disaster management, 
        monitoring rainfall, managing resources, and 
        coordinating emergency responses.
        
        Created by: **Mahad Iqbal**
        """)

def update_db_config():
    """Update database configuration from sidebar inputs"""
    st.session_state.db_config = {
        'host': st.session_state.db_host,
        'database': st.session_state.db_database,
        'user': st.session_state.db_user,
        'password': st.session_state.db_password
    }

def connect_to_database():
    """Attempt to connect to database with provided credentials"""
    try:
        db = init_connection(
            host=st.session_state.db_config['host'],
            database=st.session_state.db_config['database'],
            user=st.session_state.db_config['user'],
            password=st.session_state.db_config['password']
        )
        
        if db.connection and db.connection.is_connected():
            st.session_state.db_connected = True
            st.success("Successfully connected to database!")
            st.rerun()
        else:
            st.error("Failed to connect. Please check your credentials.")
            st.session_state.db_connected = False
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        st.session_state.db_connected = False

def auto_connect_database():
    """Automatically connect to database on startup"""
    if not st.session_state.db_connected:
        try:
            db = init_connection(
                host=st.session_state.db_config['host'],
                database=st.session_state.db_config['database'],
                user=st.session_state.db_config['user'],
                password=st.session_state.db_config['password']
            )
            
            if db.connection and db.connection.is_connected():
                st.session_state.db_connected = True
                return True
            else:
                return False
        except Exception as e:
            st.session_state.db_connected = False
            return False
    return st.session_state.db_connected

def main():
    """Main application function"""
    # Auto-connect to database on startup
    auto_connect_database()
    
    show_sidebar()
    
    # Main content area
    st.title("🌧️ Cloudburst Management System")
    st.markdown("### Smart Visualization, Analytics & Management Interface")
    
    if not st.session_state.db_connected:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Database Connection Required</strong><br>
            Please configure and connect to your MySQL database using the sidebar to access the dashboard features.
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="info-box">
                <h2>👋 Welcome to the Cloudburst Management System</h2>
                <p>This platform helps government authorities and disaster management teams efficiently 
                monitor, manage, and respond to cloudburst incidents.</p>
                
                <h3>✨ Key Features:</h3>
                <ul>
                    <li>📊 Real-time rainfall monitoring and analytics</li>
                    <li>📦 Resource inventory and distribution tracking</li>
                    <li>⚠️ Alert management and warning systems</li>
                    <li>🗺️ Interactive maps and gradient heatmaps</li>
                    <li>💾 Complete CRUD operations on all data</li>
                    <li>🤖 AI-powered chatbot assistant</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
                <h3>🚀 Getting Started</h3>
                <ol>
                    <li>Configure your database credentials in the sidebar</li>
                    <li>Click "Connect to Database"</li>
                    <li>Navigate through different sections using the page menu</li>
                    <li>Explore data visualizations and insights</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # System Overview
        st.markdown("## 🗂️ System Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📊 Data Analytics
            - Rainfall pattern analysis
            - Regional risk assessment
            - Trend visualization
            - Predictive insights
            """)
        
        with col2:
            st.markdown("""
            ### 📦 Resource Management
            - Inventory tracking
            - Distribution logging
            - Stock level monitoring
            - Location mapping
            """)
        
        with col3:
            st.markdown("""
            ### ⚠️ Alert System
            - Emergency notifications
            - Severity classification
            - Regional warnings
            - Expiry management
            """)
        
    else:
        # Connected - Show quick stats
        st.markdown("""
        <div class="success-box">
            ✅ <strong>System Ready</strong> - Database connected successfully. 
            Use the sidebar to navigate to different sections of the dashboard.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick navigation cards
        st.markdown("## 🎯 Quick Navigation")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="info-box" style="text-align: center;">
                <h3>📊</h3>
                <h4>Rainfall Analytics</h4>
                <p>View rainfall patterns and trends</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box" style="text-align: center;">
                <h3>📦</h3>
                <h4>Resources</h4>
                <p>Manage inventory and supplies</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="info-box" style="text-align: center;">
                <h3>⚠️</h3>
                <h4>Alerts</h4>
                <p>Monitor active warnings</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="info-box" style="text-align: center;">
                <h3>🤖</h3>
                <h4>AI Assistant</h4>
                <p>Get intelligent insights</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.info("💡 **Tip:** Navigate to specific sections using the page selector in the sidebar above.")

if __name__ == "__main__":
    main()
