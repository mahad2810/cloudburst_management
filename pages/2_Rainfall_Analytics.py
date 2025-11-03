"""
📊 Rainfall Analytics - Data Insights and Patterns with Mapbox
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from db.connection import init_connection
from db.queries import QueryHelper
from db.mapbox_helper import get_mapbox_visualizer
from datetime import datetime, timedelta
import sys
from pathlib import Path
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Rainfall Analytics - Cloudburst MS",
    page_icon="📊",
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

def get_rainfall_data(db, start_date=None, end_date=None, selected_regions=None):
    """Fetch rainfall data with filters"""
    try:
        query = """
        SELECT 
            rd.id,
            rd.region,
            rd.date,
            rd.rainfall_mm,
            rd.temperature_c,
            rd.humidity
        FROM rainfall_data rd
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND rd.date >= '{start_date}'"
        if end_date:
            query += f" AND rd.date <= '{end_date}'"
        if selected_regions and len(selected_regions) > 0:
            regions_str = "','".join(selected_regions)
            query += f" AND rd.region IN ('{regions_str}')"
        
        query += " ORDER BY rd.date DESC LIMIT 1000"
        
        df = db.fetch_dataframe(query)
        
        if df is not None and not df.empty:
            # Ensure date column is datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
        
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching rainfall data: {e}")
        return pd.DataFrame()

def plot_rainfall_intensity_timeline(df):
    """Create interactive rainfall intensity timeline"""
    if df.empty:
        st.info("No data available for the selected filters")
        return
    
    fig = px.line(
        df,
        x='date',
        y='rainfall_mm',
        color='region',
        title='🌧️ Rainfall Intensity Over Time',
        labels={'rainfall_mm': 'Rainfall (mm)', 'date': 'Date', 'region': 'Region'},
        template='plotly_dark',
        markers=True
    )
    
    fig.update_layout(
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    fig.update_traces(line=dict(width=2.5))
    
    st.plotly_chart(fig, use_container_width=True)

def plot_rainfall_heatmap_calendar(df):
    """Create calendar heatmap of rainfall"""
    if df.empty:
        return
    
    # Aggregate rainfall by date
    daily_rainfall = df.groupby('date')['rainfall_mm'].sum().reset_index()
    
    fig = px.density_heatmap(
        df,
        x='date',
        y='region',
        z='rainfall_mm',
        title='🗓️ Rainfall Calendar Heatmap',
        labels={'rainfall_mm': 'Rainfall (mm)', 'date': 'Date', 'region': 'Region'},
        template='plotly_dark',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def plot_rainfall_comparison(df, regions):
    """Create comparison chart for multiple regions"""
    if df.empty or not regions:
        return
    
    filtered_df = df[df['region'].isin(regions)]
    
    fig = go.Figure()
    
    for region in regions:
        region_data = filtered_df[filtered_df['region'] == region]
        fig.add_trace(go.Scatter(
            x=region_data['date'],
            y=region_data['rainfall_mm'],
            mode='lines+markers',
            name=region,
            fill='tonexty' if region != regions[0] else None
        ))
    
    fig.update_layout(
        title='📊 Regional Rainfall Comparison',
        xaxis_title='Date',
        yaxis_title='Rainfall (mm)',
        template='plotly_dark',
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_rainfall_heatmap(df, mapbox_viz=None):
    """Create geographical heatmap using Mapbox/PyDeck"""
    if df.empty:
        st.info("No data available for heatmap")
        return
    
    # Add coordinates to dataframe
    df_with_coords = df.copy()
    
    # Map coordinates without lambda
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
        st.warning("No coordinate data available for the selected regions")
        return
    
    # Aggregate rainfall by region
    agg_df = df_with_coords.groupby(['region', 'latitude', 'longitude']).agg({
        'rainfall_mm': ['mean', 'max', 'sum', 'count']
    }).reset_index()
    
    agg_df.columns = ['region', 'latitude', 'longitude', 'avg_rainfall', 'max_rainfall', 'total_rainfall', 'record_count']
    
    # Normalize rainfall for better visualization (0-1 scale)
    if agg_df['avg_rainfall'].max() > 0:
        agg_df['normalized_rainfall'] = agg_df['avg_rainfall'] / agg_df['avg_rainfall'].max()
    else:
        agg_df['normalized_rainfall'] = 0
    
    if mapbox_viz:
        # Use Mapbox for advanced visualization
        try:
            st.markdown("**🗺️ Powered by Mapbox**")
            deck = mapbox_viz.create_rainfall_heatmap(
                agg_df,
                lat_col='latitude',
                lon_col='longitude',
                intensity_col='avg_rainfall',
                center=[28.0, 80.0],  # Center of India (hill stations)
                zoom=5
            )
            
            if deck:
                st.pydeck_chart(deck)
                
                # Show legend
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Regions", len(agg_df))
                with col2:
                    st.metric("Avg Rainfall", f"{agg_df['avg_rainfall'].mean():.1f} mm")
                with col3:
                    st.metric("Max Rainfall", f"{agg_df['max_rainfall'].max():.1f} mm")
            else:
                create_mapbox_scatter_map(agg_df)
        except Exception as e:
            st.warning(f"Mapbox heatmap unavailable: {e}")
            create_mapbox_scatter_map(agg_df)
    else:
        st.info("💡 Add Mapbox token in sidebar for enhanced heatmap visualization")
        create_mapbox_scatter_map(agg_df)

def create_mapbox_scatter_map(df):
    """Create 2D Folium map centered on India with rainfall markers (no 3D globe)"""
    
    # Create Folium map centered on India
    m = folium.Map(
        location=[23.5, 78.5],  # Center of India
        zoom_start=5,
        tiles='CartoDB dark_matter'
    )
    
    # Color mapping based on rainfall intensity
    def map_rainfall_to_color(rainfall):
        if rainfall > 200:
            return 'darkred'  # Very Heavy
        elif rainfall > 150:
            return 'red'  # Heavy
        elif rainfall > 100:
            return 'orange'  # Moderate-Heavy
        elif rainfall > 50:
            return 'green'  # Moderate
        else:
            return 'lightblue'  # Light
    
    # Add circle markers for each region
    for _, row in df.iterrows():
        color = map_rainfall_to_color(row['avg_rainfall'])
        radius = min(max(row['avg_rainfall'] / 10, 8), 30)  # Scale radius
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=f"<b>{row['region']}</b><br/>Avg: {row['avg_rainfall']:.1f} mm<br/>Max: {row['max_rainfall']:.1f} mm<br/>Records: {row['record_count']}",
            tooltip=row['region'],
            color='white',
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=600)
    
    # Show color legend
    st.markdown("""
    **🌈 Rainfall Legend:**
    - 🔴 Red: Very Heavy (>200mm)
    - 🟠 Orange: Heavy (150-200mm)
    - 🟡 Yellow: Moderate-Heavy (100-150mm)
    - 🟢 Green: Moderate (50-100mm)
    - 🔵 Blue: Light (<50mm)
    """)

def plot_rainfall_distribution(df):
    """Create rainfall distribution histogram"""
    if df.empty:
        return
    
    fig = px.histogram(
        df,
        x='rainfall_mm',
        color='region',
        title='📊 Rainfall Distribution',
        labels={'rainfall_mm': 'Rainfall (mm)', 'count': 'Frequency'},
        template='plotly_dark',
        marginal='box',
        nbins=30
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def plot_temperature_humidity_correlation(df):
    """Create scatter plot for temperature vs humidity"""
    if df.empty or 'temperature_c' not in df.columns or 'humidity' not in df.columns:
        return
    
    fig = px.scatter(
        df,
        x='temperature_c',
        y='humidity',
        size='rainfall_mm',
        color='region',
        title='🌡️ Temperature vs Humidity (Size = Rainfall)',
        labels={'temperature_c': 'Temperature (°C)', 'humidity': 'Humidity (%)', 'rainfall_mm': 'Rainfall (mm)'},
        template='plotly_dark',
        hover_data=['date', 'rainfall_mm']
    )
    
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

def show_statistics(df):
    """Display statistical summary"""
    if df.empty:
        return
    
    st.markdown("### 📈 Statistical Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Avg Rainfall", f"{df['rainfall_mm'].mean():.2f} mm")
    
    with col3:
        st.metric("Max Rainfall", f"{df['rainfall_mm'].max():.2f} mm")
    
    with col4:
        st.metric("Total Regions", df['region'].nunique())
    
    # Detailed statistics
    with st.expander("📊 Detailed Statistics"):
        stats_df = df.groupby('region')['rainfall_mm'].agg([
            ('Count', 'count'),
            ('Mean', 'mean'),
            ('Median', 'median'),
            ('Std Dev', 'std'),
            ('Min', 'min'),
            ('Max', 'max')
        ]).round(2)
        
        st.dataframe(stats_df, use_container_width=True)

def plot_cloudburst_risk_heatmap(df):
    """Display geospatial gradient heatmap for cloudburst risk using Folium with YlOrRd colormap"""
    st.markdown("#### ⚠️ Cloudburst Risk Assessment Geospatial Heatmap")
    st.markdown("Interactive risk map using **YlOrRd** colormap (yellow-orange-red for heat intensity)")
    st.markdown("**Risk Formula:** Rainfall (60%) + Humidity (25%) + Temperature (15%)")
    
    # Prepare data with coordinates
    df_risk = df.copy()
    df_risk['lat'] = df_risk['region'].map(lambda x: REGION_COORDINATES.get(x, [None, None])[0])
    df_risk['lon'] = df_risk['region'].map(lambda x: REGION_COORDINATES.get(x, [None, None])[1])
    df_risk = df_risk.dropna(subset=['lat', 'lon'])
    
    # Calculate risk score
    df_risk['rainfall_score'] = (df_risk['rainfall_mm'] / 400 * 60).clip(0, 60)
    df_risk['humidity_score'] = (df_risk['humidity'] / 100 * 25).clip(0, 25)
    df_risk['temp_score'] = ((40 - df_risk['temperature_c']) / 20 * 15).clip(0, 15)
    df_risk['total_risk_score'] = df_risk['rainfall_score'] + df_risk['humidity_score'] + df_risk['temp_score']
    
    # Aggregate by region
    agg_data = df_risk.groupby(['region', 'lat', 'lon'])['total_risk_score'].mean().reset_index()
    
    # Create Folium map centered on India (2D view, no globe)
    m = folium.Map(
        location=[23.5, 78.5],  # Center of India
        zoom_start=5,
        tiles='CartoDB dark_matter',
        prefer_canvas=True
    )
    
    # Prepare heatmap data: [lat, lon, intensity]
    heat_data = [[row['lat'], row['lon'], row['total_risk_score']/100] for _, row in agg_data.iterrows()]
    
    # Add interpolation points with averaged risk scores for gradient fill
    avg_risk = agg_data['total_risk_score'].mean() / 100
    for point in INTERPOLATION_POINTS:
        # Add slight variation to interpolation points
        heat_data.append([point[0], point[1], avg_risk * 0.5])
    
    # Add heatmap layer with YlOrRd gradient (yellow-orange-red for heat intensity)
    # Increased radius and blur for better gradient fill across regions
    HeatMap(
        heat_data,
        min_opacity=0.4,
        max_opacity=0.9,
        radius=50,  # Increased for wider coverage
        blur=35,    # Increased for smoother gradients
        gradient={
            '0.0': '#ffffb2',  # Light yellow (low risk)
            '0.2': '#fed976',  # Yellow
            '0.4': '#feb24c',  # Light orange
            '0.6': '#fd8d3c',  # Orange
            '0.8': '#f03b20',  # Red
            '1.0': '#bd0026'   # Dark red (critical risk)
        }
    ).add_to(m)
    
    # Add markers with risk levels
    for _, row in agg_data.iterrows():
        score = row['total_risk_score']
        if score >= 70:
            color = 'darkred'
            icon_color = 'red'
            risk_level = 'CRITICAL'
        elif score >= 50:
            color = 'red'
            icon_color = 'orange'
            risk_level = 'HIGH'
        elif score >= 30:
            color = 'orange'
            icon_color = 'yellow'
            risk_level = 'MODERATE'
        else:
            color = 'green'
            icon_color = 'lightgreen'
            risk_level = 'LOW'
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            popup=f"<b>{row['region']}</b><br>Risk Score: {score:.1f}/100<br>Level: {risk_level}",
            color='white',
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=2
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=600)
    
    # Show top risk regions
    st.markdown("##### 🔴 Top 5 High-Risk Regions")
    top_risk = agg_data.sort_values('total_risk_score', ascending=False).head(5)
    
    cols = st.columns(5)
    for idx, (_, row) in enumerate(top_risk.iterrows()):
        with cols[idx]:
            score = row['total_risk_score']
            if score >= 70:
                color = "🔴"
                level = "Critical"
            elif score >= 50:
                color = "🟠"
                level = "High"
            elif score >= 30:
                color = "🟡"
                level = "Moderate"
            else:
                color = "🟢"
                level = "Low"
            
            st.metric(
                label=f"{color} {row['region']}",
                value=f"{score:.1f}/100",
                delta=level
            )
    
    # Interpretation guide
    with st.expander("📖 Risk Score Calculation & Colormap Interpretation"):
        st.markdown("""
        **YlOrRd Colormap (Yellow-Orange-Red for Heat Intensity):**
        - 🟡 **Light Yellow**: Low risk (0-20)
        - 🟨 **Yellow**: Caution (20-40)
        - 🟧 **Orange**: Moderate risk (40-60)
        - 🟥 **Red**: High risk (60-80)
        - � **Dark Red**: Critical risk (80-100)
        
        **Risk Score Components:**
        - **Rainfall (60%)**: Higher rainfall = higher risk
        - **Humidity (25%)**: High humidity = saturated atmosphere
        - **Temperature (15%)**: Lower temp = condensation trigger
        
        **Map Features:**
        - Click markers to see risk levels and exact scores
        - Heat intensity shows geographic risk concentration
        - Larger circles indicate higher risk areas
        """)

def main():
    """Main function for Rainfall Analytics page"""
    st.title("📊 Rainfall Analytics")
    st.markdown("### Data Insights and Pattern Analysis")
    
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
    
    # Initialize Mapbox using token from config
    import config
    mapbox_viz = None
    mapbox_token = config.MAPBOX_TOKEN if hasattr(config, 'MAPBOX_TOKEN') and config.MAPBOX_TOKEN else None
    
    if mapbox_token:
        mapbox_viz = get_mapbox_visualizer(mapbox_token)
    
    # Sidebar filters
    st.sidebar.markdown("## 🔍 Filters")
    
    # Get available regions
    try:
        regions_query = QueryHelper.get_unique_regions()
        regions_df = db.fetch_dataframe(regions_query)
        available_regions = regions_df['region'].tolist() if not regions_df.empty else []
    except:
        available_regions = []
    
    # Date range filter
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime(2025, 1, 1),  # Full data range from Jan 2025
            min_value=datetime(2025, 1, 1),
            max_value=datetime(2025, 11, 4)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime(2025, 11, 4),  # Full data range to Nov 2025
            min_value=datetime(2025, 1, 1),
            max_value=datetime(2025, 11, 4)
        )
    
    # Region filter
    selected_regions = st.sidebar.multiselect(
        "Select Regions",
        options=available_regions,
        default=available_regions[:5] if len(available_regions) >= 5 else available_regions
    )
    
    # Apply filters button
    if st.sidebar.button("🔄 Apply Filters", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Fetch data
    df = get_rainfall_data(db, start_date, end_date, selected_regions if selected_regions else None)
    
    if df.empty:
        st.warning("No rainfall data found for the selected criteria")
        st.stop()
    
    # Statistics
    show_statistics(df)
    
    st.markdown("---")
    
    # Rainfall Timeline
    plot_rainfall_intensity_timeline(df)
    
    st.markdown("---")
    
    # Geographical Heatmap
    st.markdown("### 🗺️ Geographical Rainfall Heatmap")
    if mapbox_viz:
        st.markdown("*Powered by Mapbox - Gradient intensity based on rainfall levels*")
    else:
        st.markdown("*Add Mapbox token in sidebar for enhanced visualization*")
    create_rainfall_heatmap(df, mapbox_viz)
    
    st.markdown("---")
    
    # Two-column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        plot_rainfall_distribution(df)
    
    with col2:
        plot_temperature_humidity_correlation(df)
    
    st.markdown("---")
    
    # Calendar heatmap
    plot_rainfall_heatmap_calendar(df)
    
    st.markdown("---")
    
    # Cloudburst Risk Heatmap
    st.markdown("### ⚠️ Cloudburst Risk Assessment Heatmap")
    plot_cloudburst_risk_heatmap(df)
    
    st.markdown("---")
    
    # Regional comparison
    if len(selected_regions) > 1:
        st.markdown("### 🔄 Regional Comparison")
        comparison_regions = st.multiselect(
            "Select regions to compare (max 5)",
            options=selected_regions,
            default=selected_regions[:min(3, len(selected_regions))]
        )
        
        if comparison_regions:
            plot_rainfall_comparison(df, comparison_regions)
    
    st.markdown("---")
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"rainfall_data_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.info("💡 **Insight:** Use the filters to analyze specific time periods and regions. The heatmap shows rainfall intensity gradients across locations.")

if __name__ == "__main__":
    main()
