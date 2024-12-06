import logging
import requests
import streamlit as st
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(layout='wide')

# Title of the page
st.title('Browse Available Jobs')

# Backend API base URL
API_BASE_URL = "http://localhost:5000"  # Replace with your Flask app's base URL

# Function to fetch all job postings
def fetch_all_jobs():
    try:
        response = requests.get(f"{API_BASE_URL}/job_postings")
        response.raise_for_status()
        return response.json()  # Return job data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching jobs: {e}")
        return []

# Function to fetch job postings by location
def fetch_jobs_by_location(location_id):
    try:
        response = requests.get(f"{API_BASE_URL}/job_postings/location/{location_id}")
        response.raise_for_status()
        return response.json()  # Return job data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching jobs for location {location_id}: {e}")
        return []

# Function to fetch detailed job postings with employer info
def fetch_job_postings_with_employer():
    try:
        response = requests.get(f"{API_BASE_URL}/job_postings/details")
        response.raise_for_status()
        return response.json()  # Return job data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching detailed job postings: {e}")
        return []

# Fetch all job postings
jobs = fetch_all_jobs()

# Display job postings
if jobs:
    st.write(f"### Available Jobs ({len(jobs)} found):")
    # Convert job listings to a DataFrame
    job_df = pd.DataFrame(jobs)
    if not job_df.empty:
        # Reorder and rename columns for clarity
        if 'title' in job_df and 'compensation' in job_df:
            job_df = job_df[['title', 'compensation', 'location', 'bio']].rename(
                columns={
                    'title': 'Job Title',
                    'compensation': 'Compensation',
                    'location': 'Location',
                    'bio': 'Description',
                }
            )
        st.dataframe(job_df)
    else:
        st.warning("No jobs are currently available.")
else:
    st.warning("No jobs available at this moment.")

# Add a logout button in the sidebar
st.sidebar.header('Actions')
if st.sidebar.button('Logout'):
    st.session_state.clear()  # Clear session state on logout
    st.experimental_rerun()  # Refresh the app to go back to the homepage
