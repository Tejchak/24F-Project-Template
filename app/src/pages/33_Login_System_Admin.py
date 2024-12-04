import logging
logger = logging.getLogger(__name__)
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks
import requests
from datetime import datetime, timedelta

# Set up the page configuration
st.set_page_config(layout='wide')

# Show appropriate sidebar links
SideBarLinks()

st.title('System Performance Dashboard')

# Create tabs for different metrics
tab1, tab2 = st.tabs(["Performance Metrics", "User Activity"])

with tab1:
    st.header("System Performance Over Time")
    
    # try:
        # Get performance data from the API
        # Using a sample date range for demonstration
    performance_data = requests.get('http://api:4000/performance/2024-01-01').json()
    
    # Convert to DataFrame
    df_performance = pd.DataFrame(performance_data)
    
    # Create performance metrics line chart
    fig = px.line(df_performance, 
                    x='PID',  # Date column
                    y=['CPU_Usage', 'Memory_Usage', 'Network_Usage', 'Disk_Usage'],
                    title='System Resource Usage Over Time',
                    labels={'value': 'Usage %', 'PID': 'Date'})
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display current metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Get the most recent metrics
    latest_metrics = df_performance.iloc[-1]
    
    with col1:
        st.metric("CPU Usage", f"{latest_metrics['CPU_Usage']}%")
    with col2:
        st.metric("Memory Usage", f"{latest_metrics['Memory_Usage']}%")
    with col3:
        st.metric("Network Usage", f"{latest_metrics['Network_Usage']}%")
    with col4:
        st.metric("Disk Usage", f"{latest_metrics['Disk_Usage']}%")
        
    # except Exception as e:
    #     st.error(f"Error fetching performance data: {str(e)}")

with tab2:
    st.header("User Activity Analysis")
    
    try:
        # Get user data from the API
        user_data = requests.get('http://api:4000/user').json()
        
        # Convert to DataFrame
        df_users = pd.DataFrame(user_data)
        
        # Create user metrics visualizations
        if not df_users.empty:
            # User categories distribution
            category_counts = df_users['CategoryID'].value_counts()
            fig_categories = px.pie(values=category_counts.values, 
                                  names=category_counts.index,
                                  title='User Distribution by Category')
            st.plotly_chart(fig_categories)
            
            # User registration timeline
            if 'Date_Created' in df_users.columns:
                df_users['Date_Created'] = pd.to_datetime(df_users['Date_Created'])
                daily_registrations = df_users['Date_Created'].dt.date.value_counts().sort_index()
                
                fig_registrations = px.line(x=daily_registrations.index, 
                                          y=daily_registrations.values,
                                          title='Daily User Registrations',
                                          labels={'x': 'Date', 'y': 'New Users'})
                st.plotly_chart(fig_registrations)
        
        # Display key metrics
        st.subheader("Key Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Users", len(df_users))
        with col2:
            if 'Date_Created' in df_users.columns:
                recent_users = df_users[df_users['Date_Created'] > 
                                     (datetime.now() - timedelta(days=7))].shape[0]
                st.metric("New Users (Last 7 Days)", recent_users)
            
    except Exception as e:
        st.error(f"Error fetching user data: {str(e)}")
