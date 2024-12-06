import streamlit as st
import requests
import re
import time

# Backend API base URL
API_BASE_URL = "http://api:4000"

# Set page configuration
st.set_page_config(layout='wide')

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 40px;
        font-weight: bold;
        color: #1E3D59;
        margin-bottom: 20px;
        text-align: center;
        padding: 20px;
        border-bottom: 2px solid #E8E8E8;
    }
    .profile-section {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-top: 0;
    }
    .info-label {
        font-size: 16px;
        color: #666666;
        margin-bottom: 5px;
    }
    .info-value {
        font-size: 18px;
        color: #1E3D59;
        font-weight: 500;
        margin-bottom: 15px;
    }
    .section-header {
        font-size: 24px;
        color: #1E3D59;
        margin: 0 0 20px 0;
        padding-left: 10px;
        border-left: 4px solid #17B794;
    }
    .stButton>button {
        background-color: #17B794;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 24px;
        font-weight: 500;
    }
    .success-message {
        background-color: #D4EDDA;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stTabs {
        margin-top: -1rem;
    }
    .stTab {
        margin-top: 0;
    }
    .stTabContent {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

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
    st.markdown("""
        <div class="success-message">
            ✅ Profile updated successfully!
        </div>
    """, unsafe_allow_html=True)
    del st.session_state.update_success

# Page Header
st.markdown('<h1 class="main-header">👤 Profile Management</h1>', unsafe_allow_html=True)

profile = load_profile()

if profile:
    # Create tabs for viewing and editing profile
    view_tab, edit_tab = st.tabs(["📋 View Profile", "✏️ Edit Profile"])
    
    with view_tab:
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Profile Information</h2>', unsafe_allow_html=True)
        
        # Display profile information in a more readable format
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<p class="info-label">Name</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-value">{profile.get("name", "Not provided")}</p>', unsafe_allow_html=True)
            
            st.markdown('<p class="info-label">Email</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-value">{st.session_state.verified_email}</p>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<p class="info-label">Phone Number</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-value">{profile.get("Phone_Number", "Not provided")}</p>', unsafe_allow_html=True)
            
            st.markdown('<p class="info-label">Last Updated</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-value">{profile.get("Date_Last_Login", "Unknown")}</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with edit_tab:
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Update Your Details</h2>', unsafe_allow_html=True)
        
        # Pre-fill form fields with current profile information
        name = st.text_input("Name", value=profile.get('name', ''))
        email = st.text_input("Email", value=st.session_state.verified_email)
        phone = st.text_input("Phone Number (Format: XXX-XXX-XXXX)", 
                            value=profile.get('Phone_Number', ''),
                            help="Please enter your phone number in the format: XXX-XXX-XXXX")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            # Save changes button
            if st.button("💾 Save Changes", use_container_width=True):
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
                    
                    if update_profile(st.session_state.user_id, updated_profile):
                        st.session_state.update_success = True
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("Unable to fetch your current profile information.")

# Sidebar navigation
st.sidebar.header('Navigation')

if st.sidebar.button("🏠 Back to Home"):
    st.switch_page("pages/29_Student_Home.py")

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()