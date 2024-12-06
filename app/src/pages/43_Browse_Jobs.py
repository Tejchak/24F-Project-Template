import logging
import requests
import streamlit as st
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(layout='wide')

# Sidebar Setup
def setup_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; font-size: 144px; color: #4CAF50; margin-top: -70px; margin-left: -20px;'>
            💼
        </div>
        """, unsafe_allow_html=True)
        
        st.title("Navigation")
        
        # Home button
        if st.button("🏠 Home"):
            st.switch_page("app/src/Home.py")  # Replace with your actual home page path
        
        # Back button
        if st.button("⬅️ Back"):
            st.switch_page("app/src/pages/30_dashboard.py")  # Replace with your actual back page path
        
        # Logout button
        if st.button("🚪 Logout"):
            # Clear session state if you're using it
            for key in st.session_state.keys():
                del st.session_state[key]
            st.switch_page("app/src/pages/00_login.py")  # Replace with your login page path
        
        st.divider()

# Function to fetch all job postings
def fetch_all_jobs():
    try:
        response = requests.get(f"http://localhost:4000/job_postings")  # Update to match your backend URL
        response.raise_for_status()
        return response.json()  # Return job data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching jobs: {e}")
        return []

# Main Content
def display_jobs():
    st.title("Browse Available Jobs")
    
    jobs = fetch_all_jobs()

    # Check if jobs are available
    if jobs:
        st.write(f"### Available Jobs ({len(jobs)} found):")
        
        # Convert job listings to a DataFrame
        job_df = pd.DataFrame(jobs)
        
        if not job_df.empty:
            # Reorder and rename columns for clarity
            if 'title' in job_df and 'compensation' in job_df and 'location' in job_df and 'bio' in job_df:
                job_df = job_df[['title', 'compensation', 'location', 'bio']].rename(
                    columns={
                        'title': 'Job Title',
                        'compensation': 'Compensation',
                        'location': 'Location',
                        'bio': 'Description',
                    }
                )
            
            # Add filters for Location
            location_filter = st.selectbox(
                "Filter by Location",
                options=['All'] + job_df['Location'].unique().tolist()
            )
            
            # Apply location filter if selected
            if location_filter != 'All':
                job_df = job_df[job_df['Location'] == location_filter]
            
            # Display the filtered DataFrame
            st.dataframe(job_df)
        else:
            st.warning("No jobs are currently available.")
    else:
        st.warning("No jobs available at this moment.")

# App Entry Point
if __name__ == "__main__":
    setup_sidebar()  # Configure sidebar with navigation buttons
    display_jobs()   # Show the job postings content
