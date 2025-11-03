"""
⚠️ Alert Center - Warning System Management
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.connection import init_connection
from db.queries import QueryHelper
from db.mapbox_helper import get_mapbox_visualizer
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Alert Center - Cloudburst MS",
    page_icon="⚠️",
    layout="wide"
)

# Expanded coordinates covering full region boundaries for gradient fill
REGION_COORDINATES = {
    # Original regions
    'Shimla': [31.1048, 77.1734],
    'Manali': [32.2396, 77.1887],
    'Dehradun': [30.3165, 78.0322],
    'Nainital': [29.3803, 79.4636],
    'Leh': [34.1526, 77.5771],
    'Gangtok': [27.3389, 88.6065],
    'Darjeeling': [27.0360, 88.2627],
    'Munnar': [10.0889, 77.0595],
    'Kedarnath': [30.7346, 79.0669],
    'Kargil': [34.5539, 76.1313],
    'Mussoorie': [30.4598, 78.0644],
    'Tawang': [27.5860, 91.8570],
    'Cherrapunji': [25.2630, 91.7320],
    'Pithoragarh': [29.5833, 80.2167],
    'Srinagar': [34.0837, 74.7973],
    'Aizawl': [23.7271, 92.7176],
    'Pauri': [30.1500, 78.7786],
    'Joshimath': [30.5563, 79.5647],
    'Itanagar': [27.1000, 93.6167]
}

# Additional interpolation points for gradient coverage across India
INTERPOLATION_POINTS = [
    # Himachal Pradesh region expansion
    [31.5, 76.5], [31.8, 77.0], [32.0, 77.5], [31.3, 77.8], [31.7, 76.8],
    # Uttarakhand region expansion  
    [30.0, 78.5], [30.5, 79.0], [29.8, 79.0], [30.2, 78.8], [29.5, 79.8],
    # Jammu & Kashmir expansion
    [33.5, 75.0], [34.5, 76.5], [33.8, 74.5], [34.0, 75.5], [33.2, 76.0],
    # Northeast expansion
    [26.5, 90.0], [27.0, 91.0], [26.0, 91.5], [27.5, 92.0], [26.8, 92.5],
    [25.5, 92.0], [24.8, 92.8], [27.3, 93.0], [26.2, 93.5],
    # Central Himalayas
    [29.0, 80.0], [28.5, 81.0], [29.5, 80.5], [28.8, 79.5],
    # Western Ghats expansion
    [11.0, 76.5], [10.5, 77.5], [11.5, 76.0], [10.2, 77.2], [11.8, 76.8],
    # Northern plains buffer
    [28.0, 77.0], [29.0, 78.0], [27.5, 78.5], [28.5, 79.0],
]

def get_alerts(db, active_only=False):
    """Fetch alerts from database"""
    try:
        if active_only:
            query = QueryHelper.get_active_alerts()
        else:
            query = QueryHelper.get_all_alerts()
        
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        return pd.DataFrame()

def plot_severity_distribution(df):
    """Create severity distribution pie chart"""
    if df.empty:
        st.info("No alerts to display")
        return
    
    severity_counts = df['severity'].value_counts().reset_index()
    severity_counts.columns = ['severity', 'count']
    
    colors = {
        'Critical': '#FF1744',
        'High': '#FF6F00',
        'Moderate': '#FDD835',
        'Low': '#4CAF50'
    }
    
    fig = px.pie(
        severity_counts,
        values='count',
        names='severity',
        title='⚠️ Alert Severity Distribution',
        template='plotly_dark',
        color='severity',
        color_discrete_map=colors,
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def plot_alert_timeline(df):
    """Create alert timeline visualization"""
    if df.empty:
        return
    
    # Convert dates if needed
    df['date_issued'] = pd.to_datetime(df['date_issued'])
    
    fig = px.scatter(
        df,
        x='date_issued',
        y='severity',
        size=[20] * len(df),
        color='severity',
        title='📅 Alert Timeline',
        labels={'date_issued': 'Date Issued', 'severity': 'Severity'},
        template='plotly_dark',
        color_discrete_map={
            'Critical': '#FF1744',
            'High': '#FF6F00',
            'Moderate': '#FDD835',
            'Low': '#4CAF50'
        },
        hover_data=['region', 'alert_message']
    )
    
    fig.update_layout(height=400, showlegend=True)
    fig.update_traces(marker=dict(size=15, line=dict(width=2, color='white')))
    st.plotly_chart(fig, use_container_width=True)

def plot_regional_alerts(df):
    """Create bar chart for alerts by region"""
    if df.empty:
        return
    
    regional_counts = df['region'].value_counts().reset_index()
    regional_counts.columns = ['region', 'count']
    regional_counts = regional_counts.head(10)
    
    fig = px.bar(
        regional_counts,
        x='region',
        y='count',
        title='📍 Alerts by Region (Top 10)',
        labels={'region': 'Region', 'count': 'Number of Alerts'},
        template='plotly_dark',
        color='count',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def create_alert_map(df, mapbox_viz=None):
    """Create map with alert markers and heatmap using Plotly with Mapbox"""
    if df.empty:
        st.info("No alert location data available")
        return
    
    # Add coordinates to dataframe
    df_with_coords = df.copy()
    
    # Map coordinates
    coords_list = []
    for region in df_with_coords['region']:
        coord = REGION_COORDINATES.get(region, [None, None])
        coords_list.append({'latitude': coord[0], 'longitude': coord[1]})
    
    coords_df = pd.DataFrame(coords_list)
    df_with_coords['latitude'] = coords_df['latitude']
    df_with_coords['longitude'] = coords_df['longitude']
    
    # Remove rows without coordinates
    df_with_coords = df_with_coords.dropna(subset=['latitude', 'longitude'])
    
    if df_with_coords.empty:
        st.warning("No coordinate data available for alerts")
        return
    
    # Map severity to numeric values for intensity
    severity_intensity = {
        'Severe': 4,
        'Warning': 3,
        'Info': 1
    }
    
    # Map severity to colors and sizes
    color_map = {
        'Severe': '#DC143C',
        'Warning': '#FF8C00',
        'Info': '#FFD700'
    }
    
    size_map = {
        'Severe': 18,
        'Warning': 14,
        'Info': 10
    }
    
    df_with_coords['intensity'] = df_with_coords['severity'].map(severity_intensity).fillna(1)
    df_with_coords['color'] = df_with_coords['severity'].map(color_map).fillna('#808080')
    df_with_coords['marker_size'] = df_with_coords['severity'].map(size_map).fillna(12)
    
    # Create hover text with alert message
    df_with_coords['hover_text'] = (
        '<b>' + df_with_coords['region'] + '</b><br>' +
        'Severity: ' + df_with_coords['severity'] + '<br>' +
        'Message: ' + df_with_coords['alert_message'] + '<br>' +
        'Issued: ' + df_with_coords['date_issued'].astype(str) + '<br>' +
        'Expires: ' + df_with_coords['expiry_date'].astype(str)
    )
    
    # Import config for Mapbox token
    import config
    
    # Create visualization tabs
    tab1, tab2 = st.tabs(["📍 Alert Markers", "🔥 Intensity Heatmap"])
    
    with tab1:
        # Create scatter mapbox with markers
        fig = go.Figure()
        
        for severity in ['Severe', 'Warning', 'Info']:
            df_severity = df_with_coords[df_with_coords['severity'] == severity]
            if not df_severity.empty:
                fig.add_trace(go.Scattermapbox(
                    lon=df_severity['longitude'],
                    lat=df_severity['latitude'],
                    mode='markers',
                    marker=dict(
                        size=df_severity['marker_size'],
                        color=color_map[severity],
                        opacity=0.8,
                        sizemode='diameter'
                    ),
                    text=df_severity['hover_text'],
                    name=severity,
                    hovertemplate='%{text}<extra></extra>'
                ))
        
        fig.update_layout(
            mapbox=dict(
                accesstoken=config.MAPBOX_TOKEN,
                style="dark",
                center=dict(lat=23.5, lon=78.5),  # Center of India
                zoom=5
            ),
            height=550,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(0,0,0,0.5)",
                font=dict(color="white")
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Create density heatmap
        fig_heatmap = go.Figure()
        
        # Add density mapbox for heatmap effect
        fig_heatmap.add_trace(go.Densitymapbox(
            lon=df_with_coords['longitude'],
            lat=df_with_coords['latitude'],
            z=df_with_coords['intensity'],
            radius=25,
            colorscale=[
                [0, 'rgba(255, 255, 0, 0)'],
                [0.3, 'rgba(255, 255, 0, 0.5)'],
                [0.5, 'rgba(255, 140, 0, 0.7)'],
                [0.7, 'rgba(255, 69, 0, 0.8)'],
                [1, 'rgba(220, 20, 60, 0.9)']
            ],
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Alert<br>Intensity",
                    side="right"
                ),
                tickmode="array",
                tickvals=[1, 2, 3, 4],
                ticktext=["Info", "Low", "Warning", "Severe"],
                ticks="outside"
            ),
            hovertemplate='Intensity: %{z}<extra></extra>'
        ))
        
        # Add markers on top
        fig_heatmap.add_trace(go.Scattermapbox(
            lon=df_with_coords['longitude'],
            lat=df_with_coords['latitude'],
            mode='markers',
            marker=dict(
                size=8,
                color='white',
                opacity=0.7
            ),
            text=df_with_coords['hover_text'],
            showlegend=False,
            hovertemplate='%{text}<extra></extra>'
        ))
        
        fig_heatmap.update_layout(
            mapbox=dict(
                accesstoken=config.MAPBOX_TOKEN,
                style="dark",
                center=dict(lat=23.5, lon=78.5),  # Center of India
                zoom=5
            ),
            height=550,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Add summary statistics below the map
    col1, col2, col3 = st.columns(3)
    with col1:
        severe_count = len(df_with_coords[df_with_coords['severity'] == 'Severe'])
        st.metric("🔴 Severe Alerts", severe_count)
    with col2:
        warning_count = len(df_with_coords[df_with_coords['severity'] == 'Warning'])
        st.metric("🟠 Warning Alerts", warning_count)
    with col3:
        info_count = len(df_with_coords[df_with_coords['severity'] == 'Info'])
        st.metric("🟡 Info Alerts", info_count)

def add_new_alert(db):
    """Form to add new alert"""
    st.markdown("### ➕ Issue New Alert")
    
    with st.form("add_alert_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            region = st.text_input("Region *", placeholder="e.g., Mumbai")
            severity = st.selectbox("Severity Level *", ["Low", "Moderate", "High", "Critical"])
            date_issued = st.date_input("Date Issued", value=datetime.now())
        
        with col2:
            expiry_date = st.date_input(
                "Expiry Date *",
                value=datetime.now() + timedelta(days=7)
            )
        
        alert_message = st.text_area(
            "Alert Message *",
            placeholder="Enter warning message for the public...",
            height=150
        )
        
        submitted = st.form_submit_button("🚨 Issue Alert", use_container_width=True)
        
        if submitted:
            if not region or not alert_message:
                st.error("Please fill in all required fields marked with *")
            elif date_issued > expiry_date:
                st.error("Expiry date must be after issue date")
            else:
                try:
                    query = QueryHelper.insert_alert()
                    params = (region, alert_message, severity, date_issued, expiry_date)
                    
                    if db.execute_update(query, params):
                        st.success(f"✅ Successfully issued {severity} alert for {region}")
                        st.rerun()
                    else:
                        st.error("Failed to issue alert")
                except Exception as e:
                    st.error(f"Error issuing alert: {e}")

def show_alerts_table(df, filter_severity=None):
    """Display alerts in a table with filters"""
    if df.empty:
        st.info("No alerts match the filter criteria")
        return
    
    if filter_severity and filter_severity != "All":
        df = df[df['severity'] == filter_severity]
    
    # Add color indicators
    def severity_badge(severity):
        badges = {
            'Critical': '🔴',
            'High': '🟠',
            'Moderate': '🟡',
            'Low': '🟢'
        }
        return f"{badges.get(severity, '⚪')} {severity}"
    
    df['severity_display'] = df['severity'].apply(severity_badge)
    
    # Display table
    display_df = df[['region', 'severity_display', 'alert_message', 'date_issued', 'expiry_date']].copy()
    display_df.columns = ['Region', 'Severity', 'Message', 'Issued', 'Expires']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def delete_alert(db, alerts_df):
    """Delete an alert"""
    st.markdown("### 🗑️ Delete Alert")
    
    if alerts_df.empty:
        st.info("No alerts available to delete")
        return
    
    with st.form("delete_alert_form"):
        alert_options = alerts_df.apply(
            lambda x: f"{x['region']} - {x['severity']} (ID: {x['alert_id']}, Issued: {x['date_issued']})",
            axis=1
        ).tolist()
        
        selected_alert = st.selectbox("Select Alert to Delete", alert_options)
        
        st.warning("⚠️ This action cannot be undone!")
        
        submitted = st.form_submit_button("🗑️ Delete Alert", type="primary")
        
        if submitted:
            try:
                alert_id = int(selected_alert.split("ID: ")[1].split(",")[0])
                query = QueryHelper.delete_alert()
                params = (alert_id,)
                
                if db.execute_update(query, params):
                    st.success(f"✅ Successfully deleted alert ID {alert_id}")
                    st.rerun()
                else:
                    st.error("Failed to delete alert")
            except Exception as e:
                st.error(f"Error deleting alert: {e}")

def main():
    """Main function for Alert Center page"""
    st.title("⚠️ Alert Center")
    st.markdown("### Warning System Management")
    
    # Check database connection
    if 'db_connected' not in st.session_state or not st.session_state.db_connected:
        st.warning("⚠️ Please connect to the database from the main page")
        st.stop()
    
    # Initialize database
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
    
    # Sidebar filters
    st.sidebar.markdown("## 🔍 Filters")
    show_active_only = st.sidebar.checkbox("Show Active Alerts Only", value=True)
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Fetch alerts
    alerts_df = get_alerts(db, active_only=show_active_only)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Alerts", len(alerts_df))
    
    with col2:
        critical = len(alerts_df[alerts_df['severity'] == 'Critical']) if not alerts_df.empty else 0
        st.metric("Critical", critical, delta_color="inverse")
    
    with col3:
        high = len(alerts_df[alerts_df['severity'] == 'High']) if not alerts_df.empty else 0
        st.metric("High", high, delta_color="inverse")
    
    with col4:
        regions = alerts_df['region'].nunique() if not alerts_df.empty else 0
        st.metric("Affected Regions", regions)
    
    st.markdown("---")
    
    if not alerts_df.empty:
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            plot_severity_distribution(alerts_df)
        
        with col2:
            plot_alert_timeline(alerts_df)
        
        st.markdown("---")
        
        # Regional alerts bar chart
        plot_regional_alerts(alerts_df)
        
        st.markdown("---")
        
        # Alert map
        st.markdown("### 🗺️ Alert Locations")
        st.markdown("*Marker colors indicate severity level*")
        create_alert_map(alerts_df)
        
        st.markdown("---")
        
        # Alerts table with filter
        st.markdown("### 📋 Alert Details")
        severity_filter = st.selectbox(
            "Filter by Severity",
            ["All", "Critical", "High", "Moderate", "Low"]
        )
        show_alerts_table(alerts_df, severity_filter)
        
        # Download CSV
        csv = alerts_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Alerts CSV",
            data=csv,
            file_name=f"alerts_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ No alerts found matching the filter criteria")
    
    st.markdown("---")
    
    # CRUD Operations
    tab1, tab2 = st.tabs(["➕ Add Alert", "🗑️ Delete Alert"])
    
    with tab1:
        add_new_alert(db)
    
    with tab2:
        delete_alert(db, alerts_df)
    
    # Footer
    st.info("💡 **Tip:** Critical and High severity alerts should be monitored closely and communicated to affected regions immediately.")

if __name__ == "__main__":
    main()
