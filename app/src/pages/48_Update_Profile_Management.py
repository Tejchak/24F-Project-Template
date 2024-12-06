import streamlit as st
import requests
import re

# Backend API base URL
API_BASE_URL = "http://api:4000"

# Set page configuration
st.set_page_config(layout='wide')

# Page title
st.title("Update Your Profile")

# Check if user is verified
if 'verified_email' not in st.session_state:
    st.error("Please verify your email first.")
    st.switch_page("pages/45_Update_Profile.py")

def fetch_profile(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/user/{user_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching profile information: {e}")
        return None

def update_profile(user_id, profile_data):
    try:
        response = requests.put(f"{API_BASE_URL}/user/{user_id}", json=profile_data)
        if response.status_code == 200:
            st.success("Profile updated successfully!")
        else:
            st.error(f"Failed to update profile: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating profile: {e}")

# Fetch and display current profile information
profile = fetch_profile(st.session_state.user_id)

if profile:
    st.write("### Update Your Details")
    
    # Pre-fill form fields with current profile information
    name = st.text_input("Name", value=profile.get('name', ''))
    email = st.text_input("Email", value=st.session_state.verified_email)
    phone = st.text_input("Phone Number", value=profile.get('phone_number', ''))
    address = st.text_input("Address", value=profile.get('address', ''))

    # Save changes button
    if st.button("Save Changes"):
        # Validate inputs
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            st.error("Invalid email format.")
        elif not re.match(r'^\d{10}$', phone.replace('-', '')):
            st.error("Phone number must be 10 digits.")
        else:
            updated_profile = {
                "name": name,
                "email": email,
                "phone_number": phone,
                "address": address,
                "CategoryID": 1
            }
            update_profile(st.session_state.user_id, updated_profile)
else:
    st.warning("Unable to fetch your current profile information.")

# Add a logout button in the sidebar
st.sidebar.header('Actions')
if st.sidebar.button('Logout'):
    st.session_state.clear()  # Clear session state on logout
    st.experimental_rerun()  # Refresh the app to go back to the homepage

# Back button
if st.sidebar.button("⬅️ Back"):
    st.switch_page("pages/29_Student_Home.py")