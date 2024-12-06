import logging
import requests
import streamlit as st
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(layout='wide')

# Check if user is logged in
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.error("Please log in to access this page.")
    st.switch_page("Home.py")

# Sidebar Setup
def setup_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; font-size: 144px; color: #4CAF50; margin-top: -70px; margin-left: -20px;'>
            💼
        </div>
        """, unsafe_allow_html=True)
        
        st.title("Navigation")
        
        # Back button
        if st.button("⬅️ Back"):
            st.switch_page("pages/29_Student_Home.py")  # Updated path
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.switch_page("Home.py")  # Updated path
        
        st.divider()

# Function to fetch all job postings
def fetch_all_jobs():
    try:
        response = requests.get("http://api:4000/job_postings")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching jobs: {e}")
        st.error(f"Error fetching jobs: {e}")
        return []

# Main Content
def display_jobs():
    st.title("Browse Available Jobs")
    
    jobs = fetch_all_jobs()

    # Check if jobs are available
    if jobs:
        st.write(f"### Available Jobs ({len(jobs)} found)")
        
        try:
            # Convert job listings to a DataFrame
            job_df = pd.DataFrame(jobs)
            
            if not job_df.empty:
                # Updated column mappings to match the database structure
                columns_to_display = {
                    'Title': 'Job Title',
                    'Bio': 'Description',
                    'Compensation': 'Compensation ($)',
                    'Location_ID': 'Location'
                }
                
                # Check if all required columns exist
                available_columns = [col for col in columns_to_display.keys() if col in job_df.columns]
                
                if available_columns:
                    # Select and rename available columns
                    job_df = job_df[available_columns].rename(columns={
                        col: columns_to_display[col] for col in available_columns
                    })
                    
                    # Format compensation as currency
                    if 'Compensation ($)' in job_df.columns:
                        job_df['Compensation ($)'] = job_df['Compensation ($)'].apply(
                            lambda x: f"${x:,.2f}" if pd.notnull(x) else "Not specified"
                        )
                    
                    # Add filters for Location if available
                    if 'Location' in job_df.columns:
                        location_filter = st.selectbox(
                            "Filter by Location",
                            options=['All'] + sorted(job_df['Location'].unique().tolist())
                        )
                        
                        # Apply location filter if selected
                        if location_filter != 'All':
                            job_df = job_df[job_df['Location'] == location_filter]
                    
                    # Display the filtered DataFrame
                    st.dataframe(job_df, use_container_width=True)
                else:
                    st.warning("Job data structure is not in the expected format.")
                    # Debug information
                    st.write("Available columns in data:", job_df.columns.tolist())
            else:
                st.info("No jobs are currently available.")
        except Exception as e:
            logger.error(f"Error processing job data: {e}")
            st.error(f"Error processing job data: {e}")
            # Debug information
            st.write("Raw job data structure:", jobs[0] if jobs else "No jobs data")
    else:
        st.info("No jobs available at this moment.")

# App Entry Point
if __name__ == "__main__":
    setup_sidebar()
    display_jobs()
