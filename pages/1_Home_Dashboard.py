"""
🏠 Home Dashboard - Overview and KPIs
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.connection import init_connection
from db.queries import QueryHelper
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="Home Dashboard - Cloudburst MS",
    page_icon="🏠",
    layout="wide"
)

# Apply custom CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

def get_kpi_metrics(db):
    """Fetch KPI metrics from database"""
    try:
        # Rainfall regions count
        regions_query = "SELECT COUNT(DISTINCT region) as count FROM rainfall_data"
        regions_result = db.execute_query(regions_query)
        rainfall_regions = regions_result[0]['count'] if regions_result else 0
        
        # Active alerts count
        alerts_query = QueryHelper.get_active_alerts()
        alerts_df = db.fetch_dataframe(alerts_query)
        active_alerts = len(alerts_df)
        
        # Available resources count
        resources_query = "SELECT SUM(quantity_available) as total FROM resources"
        resources_result = db.execute_query(resources_query)
        total_resources = resources_result[0]['total'] if resources_result and resources_result[0]['total'] else 0
        
        # Distribution logs count
        distributions_query = "SELECT COUNT(*) as count FROM distribution_log"
        dist_result = db.execute_query(distributions_query)
        total_distributions = dist_result[0]['count'] if dist_result else 0
        
        return {
            'rainfall_regions': rainfall_regions,
            'active_alerts': active_alerts,
            'total_resources': int(total_resources),
            'total_distributions': total_distributions
        }
    except Exception as e:
        st.error(f"Error fetching KPIs: {e}")
        return {
            'rainfall_regions': 0,
            'active_alerts': 0,
            'total_resources': 0,
            'total_distributions': 0
        }

def plot_rainfall_trends(db):
    """Create rainfall trend chart"""
    try:
        query = """
            SELECT date, region, rainfall_mm 
            FROM rainfall_data 
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            ORDER BY date
        """
        df = db.fetch_dataframe(query)
        
        if df.empty:
            st.info("No rainfall data available for the last 30 days")
            return
        
        fig = px.line(
            df, 
            x='date', 
            y='rainfall_mm', 
            color='region',
            title='📊 Rainfall Trends (Last 30 Days)',
            labels={'rainfall_mm': 'Rainfall (mm)', 'date': 'Date', 'region': 'Region'},
            template='plotly_dark'
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting rainfall trends: {e}")

def plot_alert_severity_distribution(db):
    """Create alert severity pie chart"""
    try:
        query = QueryHelper.get_alert_severity_distribution()
        df = db.fetch_dataframe(query)
        
        if df.empty:
            st.info("No active alerts to display")
            return
        
        colors = {
            'Critical': '#FF1744',
            'High': '#FF6F00',
            'Moderate': '#FDD835',
            'Low': '#4CAF50'
        }
        
        color_sequence = [colors.get(sev, '#888888') for sev in df['severity']]
        
        fig = px.pie(
            df,
            values='count',
            names='severity',
            title='⚠️ Alert Severity Distribution',
            color='severity',
            color_discrete_map=colors,
            template='plotly_dark'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting alert distribution: {e}")

def plot_resource_distribution(db):
    """Create resource distribution bar chart"""
    try:
        query = QueryHelper.get_resource_distribution()
        df = db.fetch_dataframe(query)
        
        if df.empty:
            st.info("No resource data available")
            return
        
        fig = px.bar(
            df,
            x='resource_type',
            y='total_quantity',
            title='📦 Resource Inventory by Type',
            labels={'resource_type': 'Resource Type', 'total_quantity': 'Total Quantity'},
            template='plotly_dark',
            color='total_quantity',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error plotting resource distribution: {e}")

def show_recent_alerts(db):
    """Display recent alerts table"""
    try:
        query = """
            SELECT region, alert_message, severity, date_issued, expiry_date
            FROM alerts
            WHERE expiry_date >= CURDATE()
            ORDER BY date_issued DESC
            LIMIT 5
        """
        df = db.fetch_dataframe(query)
        
        if df.empty:
            st.info("No recent alerts")
            return
        
        st.markdown("### 🚨 Recent Alerts")
        
        # Add severity badge styling
        def severity_badge(severity):
            colors = {
                'Critical': '🔴',
                'High': '🟠',
                'Moderate': '🟡',
                'Low': '🟢'
            }
            return f"{colors.get(severity, '⚪')} {severity}"
        
        df['severity'] = df['severity'].apply(severity_badge)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error fetching recent alerts: {e}")

def show_high_risk_regions(db):
    """Display high-risk regions"""
    try:
        query = QueryHelper.get_high_risk_regions()
        df = db.fetch_dataframe(query)
        
        if df.empty:
            st.success("✅ No high-risk regions currently")
            return
        
        st.markdown("### ⚠️ High Risk Regions")
        st.dataframe(
            df[['region_name', 'population', 'risk_level', 'warning_status']], 
            use_container_width=True, 
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error fetching high-risk regions: {e}")

def main():
    """Main dashboard function"""
    st.title("🏠 Home Dashboard")
    st.markdown("### Overview & Key Performance Indicators")
    
    # Check database connection
    if 'db_connected' not in st.session_state or not st.session_state.db_connected:
        st.warning("⚠️ Please connect to the database from the main page")
        st.stop()
    
    # Initialize database connection
    try:
        db = init_connection(
            host=st.session_state.db_config['host'],
            database=st.session_state.db_config['database'],
            user=st.session_state.db_config['user'],
            password=st.session_state.db_config['password']
        )
    except Exception as e:
        st.error(f"Database connection error: {e}")
        st.stop()
    
    # Refresh button
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # KPI Cards
    st.markdown("## 📊 Key Metrics")
    kpis = get_kpi_metrics(db)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="☔ Rainfall Regions Monitored",
            value=kpis['rainfall_regions'],
            delta="Active monitoring"
        )
    
    with col2:
        st.metric(
            label="⚠️ Active Alerts",
            value=kpis['active_alerts'],
            delta="Current warnings",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="📦 Resources Available",
            value=f"{kpis['total_resources']:,}",
            delta="Total units"
        )
    
    with col4:
        st.metric(
            label="🚚 Distributions Logged",
            value=kpis['total_distributions'],
            delta="All time"
        )
    
    st.markdown("---")
    
    # Visualization Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        plot_rainfall_trends(db)
    
    with col2:
        plot_alert_severity_distribution(db)
    
    st.markdown("---")
    
    # Visualization Row 2
    col1, col2 = st.columns([2, 1])
    
    with col1:
        plot_resource_distribution(db)
    
    with col2:
        st.markdown("### 📈 Quick Stats")
        
        # Additional stats
        try:
            # Average rainfall
            avg_query = "SELECT AVG(rainfall_mm) as avg_rainfall FROM rainfall_data"
            avg_result = db.execute_query(avg_query)
            avg_rainfall = round(avg_result[0]['avg_rainfall'], 2) if avg_result and avg_result[0]['avg_rainfall'] else 0
            
            st.metric("Average Rainfall", f"{avg_rainfall} mm")
            
            # Regions with warnings
            warning_query = "SELECT COUNT(*) as count FROM affected_regions WHERE warning_status = 1"
            warning_result = db.execute_query(warning_query)
            regions_warned = warning_result[0]['count'] if warning_result else 0
            
            st.metric("Regions with Warnings", regions_warned)
            
            # Low stock resources
            low_stock_query = "SELECT COUNT(*) as count FROM resources WHERE quantity_available < 100"
            low_stock_result = db.execute_query(low_stock_query)
            low_stock = low_stock_result[0]['count'] if low_stock_result else 0
            
            st.metric("Low Stock Items", low_stock, delta_color="inverse")
            
        except Exception as e:
            st.error(f"Error fetching additional stats: {e}")
    
    st.markdown("---")
    
    # Information Tables
    col1, col2 = st.columns(2)
    
    with col1:
        show_recent_alerts(db)
    
    with col2:
        show_high_risk_regions(db)
    
    # Footer
    st.markdown("---")
    st.info("💡 **Tip:** Use the sidebar to navigate to detailed analytics pages for deeper insights.")

if __name__ == "__main__":
    main()
