import streamlit as st
import requests
import pandas as pd

# Set page configuration
st.set_page_config(layout='wide')

# Page title
st.title('Job Postings')

st.write("Browse available job postings and select the one you'd like to apply for.")

# Section: Job Postings
st.subheader('Available Jobs')
try:
    # Fetch job postings from the backend API
    job_response = requests.get("http://api:4000/job_postings")  # Replace with your actual API endpoint
    if job_response.status_code == 200:
        job_data = job_response.json()
        if job_data:
            # Convert JSON response to DataFrame
            job_df = pd.DataFrame(job_data)
            # Ensure DataFrame has expected columns and display it
            if not job_df.empty and {'Post_ID', 'Title', 'Compensation', 'Location', 'Bio'}.issubset(job_df.columns):
                job_df = job_df.rename(
                    columns={
                        'Post_ID': 'Job ID',
                        'Title': 'Job Title',
                        'Compensation': 'Compensation',
                        'Location': 'Location',
                        'Bio': 'Description'
                    }
                )
                st.dataframe(job_df, use_container_width=True)
            else:
                st.write("No valid job data available.")
        else:
            st.write("No jobs available at the moment.")
    else:
        st.error(f"Failed to fetch job postings: {job_response.status_code}")
except Exception as e:
    st.error(f"An error occurred while fetching job postings: {e}")

# Add a logout button in the sidebar
st.sidebar.header('Actions')
if st.sidebar.button('Logout'):
    st.session_state.clear()  # Clear session state on logout
    st.experimental_rerun()  # Refresh the app to go back to the homepage
