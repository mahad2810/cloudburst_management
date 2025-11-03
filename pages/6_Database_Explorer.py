"""
💾 Database Explorer - Direct Data Access and CRUD Operations
"""

import streamlit as st
import pandas as pd
from db.connection import init_connection
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Database Explorer - Cloudburst MS",
    page_icon="💾",
    layout="wide"
)

TABLE_INFO = {
    'rainfall_data': {
        'display_name': '🌧️ Rainfall Data',
        'columns': ['id', 'region', 'date', 'rainfall_mm', 'temperature_c', 'humidity'],
        'pk': 'id'
    },
    'affected_regions': {
        'display_name': '🗺️ Affected Regions',
        'columns': ['region_id', 'region_name', 'population', 'risk_level', 'warning_status', 'last_update', 'report_date'],
        'pk': 'region_id'
    },
    'resources': {
        'display_name': '📦 Resources',
        'columns': ['resource_id', 'resource_type', 'quantity_available', 'location', 'status', 'last_restocked'],
        'pk': 'resource_id'
    },
    'distribution_log': {
        'display_name': '🚚 Distribution Log',
        'columns': ['log_id', 'region_id', 'resource_id', 'quantity_sent', 'date_distributed', 'distributed_by', 'received_date'],
        'pk': 'log_id'
    },
    'alerts': {
        'display_name': '⚠️ Alerts',
        'columns': ['alert_id', 'region', 'alert_message', 'severity', 'date_issued', 'expiry_date'],
        'pk': 'alert_id'
    }
}

def get_table_data(db, table_name, limit=None):
    """Fetch data from a table"""
    try:
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame()

def get_table_stats(db, table_name):
    """Get statistics for a table"""
    try:
        count_query = f"SELECT COUNT(*) as total FROM {table_name}"
        result = db.execute_query(count_query)
        total_rows = result[0]['total'] if result else 0
        
        return {'total_rows': total_rows}
    except Exception as e:
        st.error(f"Error getting stats: {e}")
        return {'total_rows': 0}

def search_table(db, table_name, search_term, columns):
    """Search across multiple columns in a table"""
    try:
        # Build search query
        conditions = []
        for col in columns:
            conditions.append(f"CAST({col} AS CHAR) LIKE '%{search_term}%'")
        
        query = f"""
            SELECT * FROM {table_name}
            WHERE {' OR '.join(conditions)}
            LIMIT 100
        """
        
        df = db.fetch_dataframe(query)
        return df
    except Exception as e:
        st.error(f"Search error: {e}")
        return pd.DataFrame()

def add_record(db, table_name):
    """Form to add a new record"""
    st.markdown(f"### ➕ Add New Record to {TABLE_INFO[table_name]['display_name']}")
    
    with st.form(f"add_{table_name}_form"):
        columns = TABLE_INFO[table_name]['columns']
        pk = TABLE_INFO[table_name]['pk']
        
        # Remove primary key from input (auto-increment)
        input_columns = [col for col in columns if col != pk or not col.endswith('_id')]
        
        values = {}
        
        # Create input fields based on table
        if table_name == 'rainfall_data':
            col1, col2 = st.columns(2)
            with col1:
                values['region'] = st.text_input("Region *")
                values['date'] = st.date_input("Date *", value=datetime.now())
                values['rainfall_mm'] = st.number_input("Rainfall (mm) *", min_value=0.0, format="%.2f")
            with col2:
                values['temperature_c'] = st.number_input("Temperature (°C)", value=25.0, format="%.2f")
                values['humidity'] = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, format="%.2f")
        
        elif table_name == 'affected_regions':
            col1, col2 = st.columns(2)
            with col1:
                values['region_name'] = st.text_input("Region Name *")
                values['population'] = st.number_input("Population *", min_value=0)
                values['risk_level'] = st.selectbox("Risk Level *", ["Low", "Moderate", "High", "Critical"])
            with col2:
                values['warning_status'] = st.checkbox("Warning Status")
                values['last_update'] = st.date_input("Last Update", value=datetime.now())
                values['report_date'] = st.date_input("Report Date", value=datetime.now())
        
        elif table_name == 'resources':
            col1, col2 = st.columns(2)
            with col1:
                values['resource_type'] = st.text_input("Resource Type *")
                values['quantity_available'] = st.number_input("Quantity *", min_value=0)
                values['location'] = st.text_input("Location *")
            with col2:
                values['status'] = st.selectbox("Status *", ["Available", "In Use", "Depleted"])
                values['last_restocked'] = st.date_input("Last Restocked", value=datetime.now())
        
        elif table_name == 'alerts':
            col1, col2 = st.columns(2)
            with col1:
                values['region'] = st.text_input("Region *")
                values['severity'] = st.selectbox("Severity *", ["Low", "Moderate", "High", "Critical"])
                values['date_issued'] = st.date_input("Date Issued", value=datetime.now())
            with col2:
                values['expiry_date'] = st.date_input("Expiry Date", value=datetime.now() + pd.Timedelta(days=7))
            values['alert_message'] = st.text_area("Alert Message *", height=100)
        
        elif table_name == 'distribution_log':
            col1, col2 = st.columns(2)
            with col1:
                values['region_id'] = st.number_input("Region ID *", min_value=1)
                values['resource_id'] = st.number_input("Resource ID *", min_value=1)
                values['quantity_sent'] = st.number_input("Quantity Sent *", min_value=1)
            with col2:
                values['date_distributed'] = st.date_input("Date Distributed", value=datetime.now())
                values['distributed_by'] = st.text_input("Distributed By *")
                values['received_date'] = st.date_input("Received Date", value=datetime.now())
        
        submitted = st.form_submit_button("💾 Add Record", use_container_width=True)
        
        if submitted:
            try:
                # Build INSERT query
                cols = ', '.join(values.keys())
                placeholders = ', '.join(['%s'] * len(values))
                query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                
                params = tuple(values.values())
                
                if db.execute_update(query, params):
                    st.success("✅ Record added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add record")
            except Exception as e:
                st.error(f"Error adding record: {e}")

def delete_record(db, table_name, record_id):
    """Delete a record"""
    try:
        pk = TABLE_INFO[table_name]['pk']
        query = f"DELETE FROM {table_name} WHERE {pk} = %s"
        
        if db.execute_update(query, (record_id,)):
            st.success(f"✅ Successfully deleted record {record_id}")
            return True
        else:
            st.error("Failed to delete record")
            return False
    except Exception as e:
        st.error(f"Error deleting record: {e}")
        return False

def main():
    """Main function for Database Explorer page"""
    st.title("💾 Database Explorer")
    st.markdown("### Direct Data Access and Management")
    
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
    
    st.markdown("---")
    
    # Table selector
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        table_options = {info['display_name']: name for name, info in TABLE_INFO.items()}
        selected_display = st.selectbox("Select Table", list(table_options.keys()))
        selected_table = table_options[selected_display]
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col3:
        show_all = st.checkbox("Show All", value=False)
    
    st.markdown("---")
    
    # Get table stats
    stats = get_table_stats(db, selected_table)
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", stats['total_rows'])
    
    with col2:
        st.metric("Table", selected_display.split()[1])
    
    with col3:
        columns_count = len(TABLE_INFO[selected_table]['columns'])
        st.metric("Columns", columns_count)
    
    with col4:
        st.metric("Primary Key", TABLE_INFO[selected_table]['pk'])
    
    st.markdown("---")
    
    # Search functionality
    search_term = st.text_input("🔍 Search", placeholder="Search across all columns...")
    
    # Fetch data
    if search_term:
        df = search_table(db, selected_table, search_term, TABLE_INFO[selected_table]['columns'])
        st.info(f"Found {len(df)} matching records")
    else:
        limit = None if show_all else 100
        df = get_table_data(db, selected_table, limit)
        
        if not show_all and stats['total_rows'] > 100:
            st.info(f"Showing first 100 of {stats['total_rows']} records. Check 'Show All' to display all records.")
    
    # Display data
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Delete record
        with st.expander("🗑️ Delete Record"):
            st.warning("⚠️ Warning: This action cannot be undone!")
            
            pk_col = TABLE_INFO[selected_table]['pk']
            
            if pk_col in df.columns:
                record_options = df[pk_col].tolist()
                selected_id = st.selectbox(f"Select {pk_col} to delete", record_options)
                
                if st.button("🗑️ Delete Selected Record", type="primary"):
                    if delete_record(db, selected_table, selected_id):
                        st.rerun()
    else:
        st.info("No records found")
    
    st.markdown("---")
    
    # Add new record
    add_record(db, selected_table)
    
    # Footer
    st.markdown("---")
    st.info("💡 **Tip:** Use the search function to quickly find specific records. Always backup your data before making bulk changes.")

if __name__ == "__main__":
    main()
