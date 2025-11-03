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

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Rainfall Analytics - Cloudburst MS",
    page_icon="📊",
    layout="wide"
)

# Coordinates for actual regions in the database
REGION_COORDINATES = {
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
    """Create scatter plot map with Mapbox style"""
    import config
    
    # Color mapping based on rainfall intensity - separate RGB columns
    def map_rainfall_to_rgb(rainfall):
        if rainfall > 200:
            return 255, 0, 0, 200  # Red - Very Heavy
        elif rainfall > 150:
            return 255, 100, 0, 200  # Orange - Heavy
        elif rainfall > 100:
            return 255, 200, 0, 200  # Yellow-Orange - Moderate-Heavy
        elif rainfall > 50:
            return 100, 200, 100, 200  # Green - Moderate
        else:
            return 0, 150, 255, 200  # Blue - Light
    
    # Apply color mapping to RGB columns
    df['r'] = df['avg_rainfall'].apply(lambda x: map_rainfall_to_rgb(x)[0])
    df['g'] = df['avg_rainfall'].apply(lambda x: map_rainfall_to_rgb(x)[1])
    df['b'] = df['avg_rainfall'].apply(lambda x: map_rainfall_to_rgb(x)[2])
    df['a'] = df['avg_rainfall'].apply(lambda x: map_rainfall_to_rgb(x)[3])
    
    # Create scatter layer
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_fill_color=["r", "g", "b", "a"],
        get_radius="avg_rainfall * 800",  # Size based on rainfall
        radius_scale=1,
        radius_min_pixels=5,
        radius_max_pixels=50,
        pickable=True,
        opacity=0.8,
    )
    
    # Create text layer for region names
    text_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_text="region",
        get_size=14,
        get_color=[255, 255, 255, 255],
        get_angle=0,
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
        pickable=False,
    )
    
    # View state
    view_state = pdk.ViewState(
        latitude=28.0,
        longitude=80.0,
        zoom=5,
        pitch=40,
        bearing=0,
    )
    
    # Check if Mapbox token is available
    mapbox_token = config.MAPBOX_TOKEN if hasattr(config, 'MAPBOX_TOKEN') and config.MAPBOX_TOKEN else None
    
    # Create deck
    if mapbox_token:
        deck = pdk.Deck(
            layers=[scatter_layer, text_layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/dark-v11",
            tooltip={
                "html": "<b>{region}</b><br/>Avg: {avg_rainfall:.1f} mm<br/>Max: {max_rainfall:.1f} mm<br/>Records: {record_count}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            },
            api_keys={"mapbox": mapbox_token}
        )
    else:
        # Fallback without Mapbox token
        deck = pdk.Deck(
            layers=[scatter_layer, text_layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{region}</b><br/>Avg: {avg_rainfall:.1f} mm<br/>Max: {max_rainfall:.1f} mm<br/>Records: {record_count}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        )
    
    st.pydeck_chart(deck)
    
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
            value=datetime(2024, 5, 1),  # Full data range from May 2024
            min_value=datetime(2024, 5, 1),
            max_value=datetime(2024, 10, 31)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime(2024, 10, 31),  # Full data range to Oct 2024
            min_value=datetime(2024, 5, 1),
            max_value=datetime(2024, 10, 31)
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
