"""
📦 Resource Overview - Inventory Management and Tracking
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from db.connection import init_connection
from db.queries import QueryHelper
from db.mapbox_helper import get_mapbox_visualizer
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Resource Overview - Cloudburst MS",
    page_icon="📦",
    layout="wide"
)

def _get_resource_status_options(db):
    """Fetch distinct resource status values from DB; fallback to CSV.
    Returns sorted list of statuses present in data.
    """
    try:
        df = db.fetch_dataframe(QueryHelper.get_distinct_values('resources', 'status'))
        values = sorted([v for v in df['value'].dropna().astype(str).unique().tolist()]) if df is not None and not df.empty else []
        if values:
            return values
    except Exception:
        pass
    # Fallback to CSV reference
    try:
        import pandas as pd
        from pathlib import Path
        csv_path = Path(__file__).parent.parent / 'csv_sheets' / 'resources.csv'
        if csv_path.exists():
            df_csv = pd.read_csv(csv_path)
            if 'status' in df_csv.columns:
                return sorted(df_csv['status'].dropna().astype(str).unique().tolist())
    except Exception:
        pass
    # Final fallback list
    return ["Available", "Low Stock", "Depleted"]

# Expanded coordinates covering full region boundaries for gradient fill
LOCATION_COORDINATES = {
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

def get_all_resources(db):
    """Fetch all resources"""
    try:
        query = QueryHelper.get_all_resources()
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.error(f"Error fetching resources: {e}")
        return pd.DataFrame()

def plot_resource_inventory(df):
    """Create bar chart for resource inventory"""
    if df.empty:
        st.info("No resource data available")
        return
    
    # Group by resource type
    resource_summary = df.groupby('resource_type')['quantity_available'].sum().reset_index()
    
    fig = px.bar(
        resource_summary,
        x='resource_type',
        y='quantity_available',
        title='📦 Resource Inventory by Type',
        labels={'resource_type': 'Resource Type', 'quantity_available': 'Quantity Available'},
        template='plotly_dark',
        color='quantity_available',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def plot_resource_status(df):
    """Create pie chart for resource status"""
    if df.empty:
        return
    
    status_summary = df.groupby('status')['resource_id'].count().reset_index()
    status_summary.columns = ['status', 'count']
    
    colors = {
        'Available': '#4CAF50',
        'Low Stock': '#FDD835',
        'Depleted': '#FF1744',
        # Support CSV variants
        'In Transit': '#29B6F6',
        'Used': '#8D6E63'
    }
    
    fig = px.pie(
        status_summary,
        values='count',
        names='status',
        title='📊 Resource Status Distribution',
        template='plotly_dark',
        color='status',
        color_discrete_map=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_resource_map(df, mapbox_viz=None):
    """Create map with resource locations using PyDeck/Mapbox"""
    if df.empty:
        st.info("No resource location data available")
        return
    
    # Add coordinates to dataframe
    df_with_coords = df.copy()
    
    # Map coordinates without lambda
    coords_list = []
    for location in df_with_coords['location']:
        coord = LOCATION_COORDINATES.get(location, [None, None])
        coords_list.append({'latitude': coord[0], 'longitude': coord[1]})
    
    coords_df = pd.DataFrame(coords_list)
    df_with_coords['latitude'] = coords_df['latitude']
    df_with_coords['longitude'] = coords_df['longitude']
    
    # Remove rows without coordinates
    df_with_coords = df_with_coords.dropna(subset=['latitude', 'longitude'])
    
    if df_with_coords.empty:
        st.warning("No coordinate data available for resource locations")
        return
    
    # Aggregate by location
    location_agg = df_with_coords.groupby(['location', 'latitude', 'longitude']).agg({
        'quantity_available': 'sum',
        'resource_id': 'count',
        'status': lambda x: (x == 'Available').sum()
    }).reset_index()
    location_agg.columns = ['location', 'latitude', 'longitude', 'total_quantity', 'resource_count', 'available_count']
    
    # Calculate status percentage
    location_agg['available_pct'] = (location_agg['available_count'] / location_agg['resource_count']) * 100
    
    # Assign colors based on availability - separate RGB columns
    def map_availability_to_rgb(pct):
        if pct > 70:
            return 0, 255, 0, 200  # Green - Good
        elif pct > 30:
            return 255, 165, 0, 200  # Orange - Warning
        else:
            return 255, 0, 0, 200  # Red - Critical
    
    # Apply color mapping to RGB columns
    location_agg['r'] = location_agg['available_pct'].apply(lambda x: map_availability_to_rgb(x)[0])
    location_agg['g'] = location_agg['available_pct'].apply(lambda x: map_availability_to_rgb(x)[1])
    location_agg['b'] = location_agg['available_pct'].apply(lambda x: map_availability_to_rgb(x)[2])
    location_agg['a'] = location_agg['available_pct'].apply(lambda x: map_availability_to_rgb(x)[3])
    
    # Create scatter layer
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=location_agg,
        get_position=["longitude", "latitude"],
        get_fill_color=["r", "g", "b", "a"],
        get_radius="total_quantity * 20",
        radius_scale=1,
        radius_min_pixels=10,
        radius_max_pixels=50,
        pickable=True,
        opacity=0.8,
    )
    
    # Create text layer
    text_layer = pdk.Layer(
        "TextLayer",
        data=location_agg,
        get_position=["longitude", "latitude"],
        get_text="location",
        get_size=12,
        get_color=[255, 255, 255, 255],
        get_angle=0,
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
    )
    
    # Create 2D Folium map centered on India (no 3D globe)
    import folium
    from streamlit_folium import st_folium
    
    m = folium.Map(
        location=[23.5, 78.5],  # Center of India
        zoom_start=5,
        tiles='CartoDB dark_matter'
    )
    
    # Add markers for each location (use location_agg which has available_pct)
    for _, row in location_agg.iterrows():
        # Determine color based on availability
        if row['available_pct'] > 70:
            color = 'green'
        elif row['available_pct'] > 30:
            color = 'orange'
        else:
            color = 'red'
        
        # Calculate radius based on quantity
        radius = min(max(row['total_quantity'] / 100, 8), 30)
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=f"<b>{row['location']}</b><br/>Resources: {row['resource_count']}<br/>Total Qty: {row['total_quantity']}<br/>Available: {row['available_pct']:.0f}%",
            tooltip=row['location'],
            color='white',
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=600)
    
    # Legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Green:** > 70% Available")
    with col2:
        st.markdown("🟠 **Orange:** 30-70% Available")
    with col3:
        st.markdown("🔴 **Red:** < 30% Available")

def show_low_stock_alerts(df, threshold=100):
    """Display low stock resources"""
    if df.empty:
        return
    
    low_stock = df[df['quantity_available'] < threshold].copy()
    
    if low_stock.empty:
        st.success("✅ All resources are adequately stocked")
        return
    
    st.markdown(f"### ⚠️ Low Stock Alert (< {threshold} units)")
    
    # Add visual indicator
    def stock_level_indicator(qty):
        if qty < 50:
            return "🔴 Critical"
        elif qty < 100:
            return "🟡 Low"
        else:
            return "🟢 Adequate"
    
    low_stock['Stock Level'] = low_stock['quantity_available'].apply(stock_level_indicator)
    
    st.dataframe(
        low_stock[['resource_type', 'location', 'quantity_available', 'Stock Level', 'status']],
        use_container_width=True,
        hide_index=True
    )

def add_new_resource(db):
    """Form to add new resource"""
    st.markdown("### ➕ Add New Resource")
    
    with st.form("add_resource_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            resource_type = st.text_input("Resource Type *", placeholder="e.g., Medical Kits")
            quantity = st.number_input("Quantity Available *", min_value=0, value=100)
            location = st.text_input("Location *", placeholder="e.g., Mumbai")
        
        with col2:
            status_options = _get_resource_status_options(db)
            status = st.selectbox("Status *", status_options)
            last_restocked = st.date_input("Last Restocked", value=datetime.now())
        
        submitted = st.form_submit_button("💾 Add Resource", use_container_width=True)
        
        if submitted:
            if not resource_type or not location:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    query = QueryHelper.insert_resource()
                    params = (resource_type, quantity, location, status, last_restocked)
                    
                    if db.execute_update(query, params):
                        st.success(f"✅ Successfully added {resource_type} to {location}")
                        st.rerun()
                    else:
                        st.error("Failed to add resource")
                except Exception as e:
                    st.error(f"Error adding resource: {e}")

def update_resource_stock(db, resource_df):
    """Form to update resource stock"""
    st.markdown("### 🔄 Update Resource Stock")
    
    if resource_df.empty:
        st.info("No resources available to update")
        return
    
    with st.form("update_stock_form"):
        # Select resource to update
        resource_options = resource_df.apply(
            lambda x: f"{x['resource_type']} - {x['location']} (ID: {x['resource_id']})", axis=1
        ).tolist()
        
        selected_resource = st.selectbox("Select Resource", resource_options)
        
        if selected_resource:
            # Extract resource ID
            resource_id = int(selected_resource.split("ID: ")[1].strip(")"))
            current_resource = resource_df[resource_df['resource_id'] == resource_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"Current Quantity: **{current_resource['quantity_available']}**")
                new_quantity = st.number_input(
                    "New Quantity",
                    min_value=0,
                    value=int(current_resource['quantity_available'])
                )
            
            with col2:
                st.info(f"Current Status: **{current_resource['status']}**")
                status_options = _get_resource_status_options(db)
                new_status = st.selectbox("New Status", status_options)
            
            last_restocked = st.date_input("Restock Date", value=datetime.now())
            
            submitted = st.form_submit_button("💾 Update Stock", use_container_width=True)
            
            if submitted:
                try:
                    query = QueryHelper.update_resource_quantity()
                    params = (new_quantity, new_status, last_restocked, resource_id)
                    
                    if db.execute_update(query, params):
                        st.success(f"✅ Successfully updated resource ID {resource_id}")
                        st.rerun()
                    else:
                        st.error("Failed to update resource")
                except Exception as e:
                    st.error(f"Error updating resource: {e}")

def main():
    """Main function for Resource Overview page"""
    st.title("📦 Resource Overview")
    st.markdown("### Inventory Management and Tracking")
    
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
    
    # Refresh button
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Fetch resources
    resources_df = get_all_resources(db)
    
    if resources_df.empty:
        st.warning("No resource data available")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Resources", len(resources_df))
        
        with col2:
            st.metric("Total Quantity", f"{resources_df['quantity_available'].sum():,}")
        
        with col3:
            available = len(resources_df[resources_df['status'] == 'Available'])
            st.metric("Available", available)
        
        with col4:
            depleted = len(resources_df[resources_df['status'] == 'Depleted'])
            st.metric("Depleted", depleted, delta_color="inverse")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns([2, 1])
        
        with col1:
            plot_resource_inventory(resources_df)
        
        with col2:
            plot_resource_status(resources_df)
        
        st.markdown("---")
        
        # Low stock alerts
        show_low_stock_alerts(resources_df, threshold=100)
        
        st.markdown("---")
        
        # Resource map
        st.markdown("### 🗺️ Resource Locations")
        st.markdown("*Pin colors: Green = Well-stocked, Orange = Moderate, Red = Low stock*")
        create_resource_map(resources_df)
        
        st.markdown("---")
        
        # CRUD Operations
        tab1, tab2, tab3 = st.tabs(["➕ Add Resource", "🔄 Update Stock", "📋 View All"])
        
        with tab1:
            add_new_resource(db)
        
        with tab2:
            update_resource_stock(db, resources_df)
        
        with tab3:
            st.markdown("### 📋 All Resources")
            st.dataframe(resources_df, use_container_width=True, hide_index=True)
            
            # Download CSV
            csv = resources_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"resources_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.info("💡 **Tip:** Monitor low stock alerts regularly and update inventory after distributions.")

if __name__ == "__main__":
    main()
