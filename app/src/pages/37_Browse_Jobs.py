import streamlit as st
import requests
import pandas as pd

st.title("Browse Available Jobs")
st.write("Explore job opportunities that match your interests and skills.")

# Check if student is logged in
if 'student_id' in st.session_state:
    student_id = st.session_state.student_id

    # Fetch available jobs
    try:
        response = requests.get(f"http://api:4000/students/{student_id}/jobs")
        response.raise_for_status()
        jobs = response.json()

        if jobs:
            st.success("Available jobs retrieved successfully!")
            df = pd.DataFrame(jobs)
            st.dataframe(df[['job_posting_id', 'title', 'compensation', 'location_id']], use_container_width=True)
        else:
            st.warning("No available jobs at the moment.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching jobs: {e}")
else:
    st.error("Please log in to access this page.")
