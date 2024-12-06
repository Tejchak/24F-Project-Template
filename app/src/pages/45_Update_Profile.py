import streamlit as st
import requests
import re

# Backend API base URL
API_BASE_URL = "http://api:4000"  

# Set page configuration
st.set_page_config(layout='wide')

# Page title
st.title("Update Your Profile")

# Check if email is verified
if 'verified_email' not in st.session_state:
    st.write("Please verify your email to continue.")
    user_email = st.text_input("Enter your email (E.x: klaus.mikaelson@example.com)", 
                              placeholder="klaus.mikaelson@example.com")

    if st.button("Verify Email"):
        if user_email:
            try:
                # Check if the email exists in the database
                response = requests.get(f'{API_BASE_URL}/users/email/{user_email}')
                response.raise_for_status()
                user_data = response.json()

                # If the email is found, store user ID and email in session state
                st.session_state.user_id = user_data['UserID']
                st.session_state.verified_email = user_email
                st.success("Email verified successfully!")
                st.switch_page("pages/48_Update_Profile_Management.py")

            except requests.exceptions.HTTPError:
                st.error("Email not found in the database.")
        else:
            st.warning("Please enter a valid email.")
else:
    st.switch_page("pages/48_Update_Profile_Management.py")
