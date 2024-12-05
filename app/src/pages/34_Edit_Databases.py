import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks
import requests
from datetime import datetime

# Set up the page configuration
st.set_page_config(layout='wide')

# Show appropriate sidebar links
SideBarLinks()

# Add logout button to sidebar
with st.sidebar:
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.switch_page("app/src/Home.py")

st.title('Database Management')

# Select table to manage
table_options = ['Performance', 'User', 'City', 'Category', 'Airport']
selected_table = st.selectbox('Select Table to Manage:', table_options)

# Create tabs for different operations
tab1, tab2, tab3 = st.tabs(["Add Data", "Update Data", "Delete Data"])

with tab1:
    st.header(f"Add New {selected_table} Entry")
    
    if selected_table == 'Performance':
        date = st.date_input("Date")
        cpu_usage = st.number_input("CPU Usage (%)", min_value=0, max_value=100)
        memory_usage = st.number_input("Memory Usage (%)", min_value=0, max_value=100)
        network_usage = st.number_input("Network Usage (%)", min_value=0, max_value=100)
        disk_usage = st.number_input("Disk Usage (%)", min_value=0, max_value=100)
        
        if st.button("Add Performance Entry"):
            try:
                response = requests.post('http://api:4000/performance/add', json={
                    'date': date.strftime('%Y-%m-%d'),
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'network_usage': network_usage,
                    'disk_usage': disk_usage
                })
                if response.status_code == 200:
                    st.success("Entry added successfully!")
                else:
                    st.error("Failed to add entry")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab2:
    st.header(f"Update Existing {selected_table} Entry")
    
    if selected_table == 'Performance':
        # Get existing dates
        try:
            dates_response = requests.get('http://api:4000/performance/dates')
            if dates_response.status_code == 200:
                dates = dates_response.json()
                selected_date = st.selectbox("Select Date to Update", dates)
                
                if selected_date:
                    cpu_usage = st.number_input("New CPU Usage (%)", min_value=0, max_value=100)
                    memory_usage = st.number_input("New Memory Usage (%)", min_value=0, max_value=100)
                    network_usage = st.number_input("New Network Usage (%)", min_value=0, max_value=100)
                    disk_usage = st.number_input("New Disk Usage (%)", min_value=0, max_value=100)
                    
                    if st.button("Update Entry"):
                        try:
                            response = requests.put(f'http://api:4000/performance/update/{selected_date}', json={
                                'cpu_usage': cpu_usage,
                                'memory_usage': memory_usage,
                                'network_usage': network_usage,
                                'disk_usage': disk_usage
                            })
                            if response.status_code == 200:
                                st.success("Entry updated successfully!")
                            else:
                                st.error("Failed to update entry")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching dates: {str(e)}")

with tab3:
    st.header(f"Delete {selected_table} Entry")
    
    if selected_table == 'Performance':
        try:
            dates_response = requests.get('http://api:4000/performance/dates')
            if dates_response.status_code == 200:
                dates = dates_response.json()
                selected_date = st.selectbox("Select Date to Delete", dates)
                
                if selected_date:
                    if st.button("Delete Entry", type="primary"):
                        try:
                            response = requests.delete(f'http://api:4000/performance/delete/{selected_date}')
                            if response.status_code == 200:
                                st.success("Entry deleted successfully!")
                            else:
                                st.error("Failed to delete entry")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching dates: {str(e)}")
