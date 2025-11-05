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

def predict_cloudburst_risk(db):
    """Predict cloudburst risk based on recent rainfall patterns"""
    try:
        # Get recent rainfall data (last 7 days)
        query = """
            SELECT region, 
                   AVG(rainfall_mm) as avg_rainfall,
                   MAX(rainfall_mm) as max_rainfall,
                   COUNT(*) as data_points
            FROM rainfall_data
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY region
            HAVING avg_rainfall > 0
            ORDER BY avg_rainfall DESC
        """
        df = db.fetch_dataframe(query)
        
        if df.empty:
            return pd.DataFrame()
        
        # Cloudburst risk prediction logic
        # High risk: avg > 200mm or max > 300mm
        # Moderate risk: avg > 150mm or max > 250mm
        # Low risk: avg > 100mm or max > 200mm
        
        def calculate_risk(row):
            avg = row['avg_rainfall']
            max_val = row['max_rainfall']
            
            if avg > 200 or max_val > 300:
                return 'High', '🔴', 90
            elif avg > 150 or max_val > 250:
                return 'Moderate', '🟠', 65
            elif avg > 100 or max_val > 200:
                return 'Low', '🟡', 40
            else:
                return 'Minimal', '🟢', 15
        
        df[['risk_level', 'indicator', 'risk_score']] = df.apply(
            lambda row: pd.Series(calculate_risk(row)), axis=1
        )
        
        return df
        
    except Exception as e:
        st.error(f"Error predicting cloudburst risk: {e}")
        return pd.DataFrame()

def display_cloudburst_predictions(db):
    """Display cloudburst prediction dashboard"""
    st.markdown("### 🌩️ Cloudburst Risk Prediction")
    st.markdown("*Based on 7-day rainfall pattern analysis*")
    
    predictions_df = predict_cloudburst_risk(db)
    
    if predictions_df.empty:
        st.info("📊 Insufficient data for predictions. Need at least 7 days of rainfall data.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    high_risk_count = len(predictions_df[predictions_df['risk_level'] == 'High'])
    moderate_risk_count = len(predictions_df[predictions_df['risk_level'] == 'Moderate'])
    low_risk_count = len(predictions_df[predictions_df['risk_level'] == 'Low'])
    safe_count = len(predictions_df[predictions_df['risk_level'] == 'Minimal'])
    
    with col1:
        st.metric("🔴 High Risk Regions", high_risk_count)
    with col2:
        st.metric("🟠 Moderate Risk", moderate_risk_count)
    with col3:
        st.metric("🟡 Low Risk", low_risk_count)
    with col4:
        st.metric("🟢 Safe Regions", safe_count)
    
    # Risk visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart of risk scores by region
        fig = px.bar(
            predictions_df.head(10),
            x='region',
            y='risk_score',
            color='risk_level',
            color_discrete_map={
                'High': '#FF4444',
                'Moderate': '#FFA500',
                'Low': '#FFD700',
                'Minimal': '#4CAF50'
            },
            title='Top 10 Regions by Cloudburst Risk Score',
            labels={'risk_score': 'Risk Score (%)', 'region': 'Region'},
            hover_data=['avg_rainfall', 'max_rainfall']
        )
        fig.update_layout(
            template='plotly_dark',
            height=350,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk level distribution pie chart
        risk_dist = predictions_df['risk_level'].value_counts().reset_index()
        risk_dist.columns = ['Risk Level', 'Count']
        
        fig_pie = px.pie(
            risk_dist,
            values='Count',
            names='Risk Level',
            title='Risk Distribution',
            color='Risk Level',
            color_discrete_map={
                'High': '#FF4444',
                'Moderate': '#FFA500',
                'Low': '#FFD700',
                'Minimal': '#4CAF50'
            }
        )
        fig_pie.update_layout(template='plotly_dark', height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed risk table
    with st.expander("📋 Detailed Risk Assessment"):
        display_df = predictions_df[['indicator', 'region', 'risk_level', 'risk_score', 'avg_rainfall', 'max_rainfall']].copy()
        display_df.columns = ['', 'Region', 'Risk Level', 'Risk Score (%)', 'Avg Rainfall (mm)', 'Max Rainfall (mm)']
        display_df = display_df.sort_values('Risk Score (%)', ascending=False)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                '': st.column_config.TextColumn('', width='small'),
                'Risk Score (%)': st.column_config.ProgressColumn(
                    'Risk Score (%)',
                    min_value=0,
                    max_value=100,
                    format='%d%%'
                )
            }
        )

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
        
        # Limit number of regions displayed to avoid clutter
        top_regions = df.groupby('region')['rainfall_mm'].mean().nlargest(8).index
        df_filtered = df[df['region'].isin(top_regions)]
        
        fig = px.line(
            df_filtered, 
            x='date', 
            y='rainfall_mm', 
            color='region',
            title='📊 Rainfall Trends (Last 30 Days) - Top 8 Regions by Average',
            labels={'rainfall_mm': 'Rainfall (mm)', 'date': 'Date', 'region': 'Region'},
            template='plotly_dark'
        )
        
        fig.update_layout(
            height=450,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="rgba(255,255,255,0.3)",
                borderwidth=1
            ),
            margin=dict(r=150, l=50, t=50, b=50),
            xaxis_title="Date",
            yaxis_title="Rainfall (mm)"
        )
        
        fig.update_traces(line=dict(width=2.5), marker=dict(size=4))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show info about filtered regions
        total_regions = df['region'].nunique()
        if total_regions > 8:
            st.caption(f"ℹ️ Showing top 8 regions out of {total_regions} total regions with highest average rainfall")
            
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
    
    # Cloudburst Prediction Section
    display_cloudburst_predictions(db)
    
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
