import streamlit as st
import requests
import re

# Backend API base URL
API_BASE_URL = "http://localhost:4000"  

# Set page configuration
st.set_page_config(layout='wide')

# Page title
st.title("Update Your Profile")

# Ensure user is logged in and their ID is in the session
if 'user_id' not in st.session_state:
    st.error("You must be logged in to update your profile.")
    st.stop()

# Function to fetch current profile information
def fetch_profile(user_id):
    try:
        # Fetch user details from the backend using GET /user/<user_id>
        response = requests.get(f"{API_BASE_URL}/user/{user_id}")
        response.raise_for_status()
        return response.json()  # Return user profile data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching profile information: {e}")
        return None

# Function to update profile information
def update_profile(user_id, profile_data):
    try:
        # Send updated user data to the backend using PUT /user/<user_id>
        response = requests.put(f"{API_BASE_URL}/user/{user_id}", json=profile_data)
        if response.status_code == 200:
            st.success("Profile updated successfully!")
        else:
            st.error(f"Failed to update profile: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating profile: {e}")

# Fetch and display current profile information
user_id = st.session_state['user_id']
profile = fetch_profile(user_id)

if profile:
    st.write("### Update Your Details")
    
    # Pre-fill form fields with current profile information
    name = st.text_input("Name", value=profile.get('name', ''))
    email = st.text_input("Email", value=profile.get('email', ''))
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
            }
            update_profile(user_id, updated_profile)
else:
    st.warning("Unable to fetch your current profile information.")

# Add a logout button in the sidebar
st.sidebar.header('Actions')
if st.sidebar.button('Logout'):
    st.session_state.clear()  # Clear session state on logout
    st.experimental_rerun()  # Refresh the app to go back to the homepage
