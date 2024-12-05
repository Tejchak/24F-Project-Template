import streamlit as st
import requests
import pandas as pd

st.title("Application Status")
st.write("Check the status of your submitted applications.")

if 'student_id' in st.session_state:
    student_id = st.session_state.student_id

    try:
        response = requests.get(f"http://api:4000/students/{student_id}/applications")
        response.raise_for_status()
        applications = response.json()

        if applications:
            df = pd.DataFrame(applications)
            st.dataframe(df[['job_title', 'status', 'application_date']], use_container_width=True)
        else:
            st.warning("You have not submitted any applications yet.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching applications: {e}")
else:
    st.error("Please log in to access this page.")
