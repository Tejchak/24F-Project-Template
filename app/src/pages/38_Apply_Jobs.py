import streamlit as st
import requests

st.title("Apply for a Job")
st.write("Submit an application for a job posting.")

if 'student_id' in st.session_state:
    student_id = st.session_state.student_id

    # Fetch available jobs
    try:
        response = requests.get(f"http://api:4000/students/{student_id}/jobs")
        response.raise_for_status()
        jobs = response.json()

        if jobs:
            job_id = st.selectbox("Select a job to apply for", [job['job_posting_id'] for job in jobs])
            if st.button("Apply"):
                try:
                    apply_response = requests.post(
                        f"http://api:4000/students/{student_id}/apply",
                        json={"job_posting_id": job_id}
                    )
                    apply_response.raise_for_status()
                    st.success("Application submitted successfully!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error applying for the job: {e}")
        else:
            st.warning("No available jobs to apply for.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching jobs: {e}")
else:
    st.error("Please log in to access this page.")
