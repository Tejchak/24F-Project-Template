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

# Add logout button to sidebar
with st.sidebar:
    st.divider()  # Add a visual separator
    if st.button("🚪 Logout", use_container_width=True):
        # Clear any session state if you're using it
        for key in st.session_state.keys():
            del st.session_state[key]
        # Redirect to home page
        st.switch_page("Home.py")

st.title('System Performance Dashboard')

# Create tabs for different metrics
tab1, tab2 = st.tabs(["Performance Metrics", "User Activity"])

with tab1:
    st.header("System Performance Over Time")
    
    # Get available dates from the API
    try:
        dates_response = requests.get('http://api:4000/performance/dates')
        if dates_response.status_code == 200:
            available_dates = dates_response.json()
            selected_date = st.selectbox(
                "Select Date",
                options=available_dates,
                format_func=lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%B %d, %Y'),
                index=0 if available_dates else None
            )
            
            if selected_date:
                response = requests.get(f'http://api:4000/performance/{selected_date}')
                if response.status_code == 200:
                    performance_data = response.json()
                    
                    if performance_data:
                        
                        # Convert to DataFrame
                        df_performance = pd.DataFrame(performance_data)
                        
                        if not df_performance.empty:
                            # Get the latest metrics for the bar chart
                            latest_metrics = df_performance.iloc[-1]
                            
                            # Create a bar chart for all metrics
                            metrics_data = {
                                'Metric': ['CPU', 'Memory', 'Network', 'Disk'],
                                'Usage': [
                                    latest_metrics['CPU_Usage'],
                                    latest_metrics['Memory_Usage'],
                                    latest_metrics['Network_Usage'],
                                    latest_metrics['Disk_Usage']
                                ]
                            }
                            df_metrics = pd.DataFrame(metrics_data)
                            
                            fig = px.bar(df_metrics,
                                       x='Metric',
                                       y='Usage',
                                       title='System Resource Usage',
                                       labels={'Usage': 'Usage %'},
                                       color='Metric')
                            
                            # Update layout to make it more readable
                            fig.update_layout(
                                showlegend=False,
                                yaxis_range=[0, 100]  # Set y-axis from 0 to 100%
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display current metrics in columns
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("CPU Usage", f"{latest_metrics['CPU_Usage']}%")
                            with col2:
                                st.metric("Memory Usage", f"{latest_metrics['Memory_Usage']}%")
                            with col3:
                                st.metric("Network Usage", f"{latest_metrics['Network_Usage']}%")
                            with col4:
                                st.metric("Disk Usage", f"{latest_metrics['Disk_Usage']}%")
                        else:
                            st.warning("No performance data available for the selected date")
                    else:
                        st.warning("No data returned from the API")
                else:
                    st.error(f"Error fetching performance data: Status code {response.status_code}")
        else:
            st.error("Could not fetch available dates")
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
            
   
with tab2:
    st.header("User Activity Analysis")
    
    # Get user data from the API
    user_data = requests.get('http://api:4000/user').json()
    
    # Convert to DataFrame
    df_users = pd.DataFrame(user_data)
    print(df_users)
    
    # Create user metrics visualizations
    if not df_users.empty:
        # User categories distribution
        category_counts = df_users['CategoryName'].value_counts()
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
                                    (datetime.now() - timedelta(days=30))].shape[0]
            st.metric("New Users (Last 30 Days)", recent_users)
            