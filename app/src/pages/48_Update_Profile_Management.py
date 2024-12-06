import streamlit as st
import requests
import re
import time

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
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating profile: {e}")
        return False

def format_phone_number(phone):
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    # Format as XXX-XXX-XXXX
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return digits

# Fetch profile information
def load_profile():
    return fetch_profile(st.session_state.user_id)

# Check for update success message
if 'update_success' in st.session_state and st.session_state.update_success:
    st.success("Profile updated successfully!")
    # Clear the success message flag
    del st.session_state.update_success
    
profile = load_profile()

if profile:
    # Create tabs for viewing and editing profile
    view_tab, edit_tab = st.tabs(["View Profile", "Edit Profile"])
    
    with view_tab:
        st.write("### Your Profile Information")
        
        # Display profile information in a more readable format
        st.write("**Name:**", profile.get('name', 'Not provided'))
        st.write("**Email:**", st.session_state.verified_email)
        st.write("**Phone Number:**", profile.get('Phone_Number', 'Not provided'))
        
        # Add a divider for better visual separation
        st.divider()
        st.write("*Last updated: " + profile.get('Date_Last_Login', 'Unknown') + "*")
    
    with edit_tab:
        st.write("### Update Your Details")
        
        # Pre-fill form fields with current profile information
        name = st.text_input("Name", value=profile.get('name', ''))
        email = st.text_input("Email", value=st.session_state.verified_email)
        phone = st.text_input("Phone Number (Format: XXX-XXX-XXXX)", value=profile.get('Phone_Number', ''))

        # Save changes button
        if st.button("Save Changes"):
            # Validate inputs
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                st.error("Invalid email format.")
            elif not re.match(r'^\d{3}-\d{3}-\d{4}$', format_phone_number(phone)):
                st.error("Phone number must be in format XXX-XXX-XXXX")
            else:
                updated_profile = {
                    "name": name,
                    "email": email,
                    "Phone_Number": format_phone_number(phone),
                    "CategoryID": 1
                }
                
                # Update the profile
                if update_profile(st.session_state.user_id, updated_profile):
                    # Set success flag in session state
                    st.session_state.update_success = True
                    # Add a small delay to ensure the message is visible
                    time.sleep(0.5)
                    st.rerun()
else:
    st.warning("Unable to fetch your current profile information.")

# Add a logout button in the sidebar
st.sidebar.header('Actions')
if st.sidebar.button('Logout'):
    st.session_state.clear()  # Clear session state on logout
    st.rerun()  # Refresh the app to go back to the homepage

# Back button
if st.sidebar.button("⬅️ Back"):
    st.switch_page("pages/29_Student_Home.py")