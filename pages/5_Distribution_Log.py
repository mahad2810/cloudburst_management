"""
🚚 Distribution Log - Aid Tracking and Management
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

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Distribution Log - Cloudburst MS",
    page_icon="🚚",
    layout="wide"
)

def get_distributions(db, start_date=None, end_date=None):
    """Fetch distribution records"""
    try:
        if start_date and end_date:
            query = QueryHelper.get_distributions_by_date_range(start_date, end_date)
        else:
            query = QueryHelper.get_all_distributions()
        
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.error(f"Error fetching distributions: {e}")
        return pd.DataFrame()

def plot_distribution_timeline(df):
    """Create timeline chart for distributions"""
    if df.empty:
        st.info("No distribution data available")
        return
    
    df['date_distributed'] = pd.to_datetime(df['date_distributed'])
    
    daily_dist = df.groupby('date_distributed')['quantity_sent'].sum().reset_index()
    
    fig = px.line(
        daily_dist,
        x='date_distributed',
        y='quantity_sent',
        title='📦 Distribution Volume Over Time',
        labels={'date_distributed': 'Date', 'quantity_sent': 'Quantity Distributed'},
        template='plotly_dark',
        markers=True
    )
    
    fig.update_traces(line=dict(width=3, color='#4FC3F7'))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def plot_regional_distribution(df):
    """Create stacked bar chart for region-wise distribution"""
    if df.empty:
        return
    
    regional_dist = df.groupby(['region_name', 'resource_type'])['quantity_sent'].sum().reset_index()
    
    fig = px.bar(
        regional_dist,
        x='region_name',
        y='quantity_sent',
        color='resource_type',
        title='🌍 Region-wise Distribution (by Resource Type)',
        labels={'region_name': 'Region', 'quantity_sent': 'Quantity', 'resource_type': 'Resource'},
        template='plotly_dark',
        barmode='stack'
    )
    
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

def plot_resource_distribution(df):
    """Create pie chart for resource type distribution"""
    if df.empty:
        return
    
    resource_dist = df.groupby('resource_type')['quantity_sent'].sum().reset_index()
    
    fig = px.pie(
        resource_dist,
        values='quantity_sent',
        names='resource_type',
        title='📊 Distribution by Resource Type',
        template='plotly_dark'
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def add_distribution_log(db):
    """Form to add new distribution record"""
    st.markdown("### ➕ Log New Distribution")
    
    # Get regions and resources
    try:
        regions_query = "SELECT region_id, region_name FROM affected_regions ORDER BY region_name"
        regions_df = db.fetch_dataframe(regions_query)
        
        resources_query = "SELECT resource_id, resource_type FROM resources ORDER BY resource_type"
        resources_df = db.fetch_dataframe(resources_query)
        
        if regions_df.empty or resources_df.empty:
            st.warning("⚠️ No regions or resources available. Please add them first.")
            return
        
        region_options = {f"{row['region_name']} (ID: {row['region_id']})": row['region_id'] 
                         for _, row in regions_df.iterrows()}
        resource_options = {f"{row['resource_type']} (ID: {row['resource_id']})": row['resource_id'] 
                           for _, row in resources_df.iterrows()}
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    with st.form("add_distribution_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_region = st.selectbox("Select Region *", list(region_options.keys()))
            selected_resource = st.selectbox("Select Resource *", list(resource_options.keys()))
            quantity = st.number_input("Quantity Sent *", min_value=1, value=50)
        
        with col2:
            date_distributed = st.date_input("Distribution Date *", value=datetime.now())
            distributed_by = st.text_input("Distributed By *", placeholder="Official name")
            received_date = st.date_input("Received Date", value=datetime.now())
        
        submitted = st.form_submit_button("📦 Log Distribution", use_container_width=True)
        
        if submitted:
            if not distributed_by:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    region_id = region_options[selected_region]
                    resource_id = resource_options[selected_resource]
                    
                    query = QueryHelper.insert_distribution()
                    params = (region_id, resource_id, quantity, date_distributed, 
                             distributed_by, received_date)
                    
                    if db.execute_update(query, params):
                        st.success("✅ Successfully logged distribution")
                        st.rerun()
                    else:
                        st.error("Failed to log distribution")
                except Exception as e:
                    st.error(f"Error logging distribution: {e}")

def main():
    """Main function for Distribution Log page"""
    st.title("🚚 Distribution Log")
    st.markdown("### Aid Tracking and Management")
    
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
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )
    
    if st.sidebar.button("🔄 Apply Filters", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Fetch distributions
    distributions_df = get_distributions(db, start_date, end_date)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Distributions", len(distributions_df))
    
    with col2:
        total_qty = distributions_df['quantity_sent'].sum() if not distributions_df.empty else 0
        st.metric("Total Quantity", f"{total_qty:,}")
    
    with col3:
        regions = distributions_df['region_name'].nunique() if not distributions_df.empty else 0
        st.metric("Regions Served", regions)
    
    with col4:
        resources = distributions_df['resource_type'].nunique() if not distributions_df.empty else 0
        st.metric("Resource Types", resources)
    
    st.markdown("---")
    
    if not distributions_df.empty:
        # Timeline chart
        plot_distribution_timeline(distributions_df)
        
        st.markdown("---")
        
        # Two-column layout for charts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            plot_regional_distribution(distributions_df)
        
        with col2:
            plot_resource_distribution(distributions_df)
        
        st.markdown("---")
        
        # Distribution table
        st.markdown("### 📋 Distribution Records")
        
        # Add search
        search = st.text_input("🔍 Search", placeholder="Search by region, resource, or official name...")
        
        if search:
            mask = (
                distributions_df['region_name'].str.contains(search, case=False, na=False) |
                distributions_df['resource_type'].str.contains(search, case=False, na=False) |
                distributions_df['distributed_by'].str.contains(search, case=False, na=False)
            )
            filtered_df = distributions_df[mask]
        else:
            filtered_df = distributions_df
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # Download CSV
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"distributions_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
    else:
        st.info("No distribution records found for the selected date range")
    
    st.markdown("---")
    
    # Add new distribution
    add_distribution_log(db)
    
    # Footer
    st.info("💡 **Tip:** Keep distribution logs updated in real-time for accurate tracking and resource planning.")

if __name__ == "__main__":
    main()
