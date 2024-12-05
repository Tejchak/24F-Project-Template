import streamlit as st
import requests

# Set page title
st.set_page_config(page_title="Email Verification", layout="wide")

# Title and description
st.title("Email Verification")
st.write("Please enter your email to verify your account.")

# Input for email
user_email = st.text_input("Enter your email (E.x: klaus.mikaelson@example.com)", placeholder="klaus.mikaelson@example.com")

if st.button("Verify Email"):
    if user_email:
        try:
            # Check if the email exists in the database
            response = requests.get(f'http://api:4000/users/email/{user_email}')
            response.raise_for_status()
            user_data = response.json()

            # If the email is found, store user ID in session state
            user_id = user_data['UserID']  # Assuming the response contains UserID
            st.session_state.user_id = user_id  # Store user ID in session state
            
            st.session_state.page = "job_postings_management"  # Set session state for redirection
            st.switch_page('pages/13_Job_Postings_Management.py')

        except requests.exceptions.HTTPError:
            st.error("Email not found in the database.")
    else:
        st.warning("Please enter a valid email.")
