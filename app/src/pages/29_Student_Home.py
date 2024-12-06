import logging
logger = logging.getLogger(__name__)

import streamlit as st
import sys
import os
# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.nav import SideBarLinks


st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

# Create a clean header section with custom styling
if 'first_name' in st.session_state:
    st.markdown(f"""
        <h1 style='text-align: center; color: #1E3D59; padding-top: 1rem; padding-bottom: 0; margin-bottom: 0;'>
            Welcome, {st.session_state['first_name']}!
        </h1>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <h1 style='text-align: center; color: #1E3D59; padding-top: 1rem; padding-bottom: 0; margin-bottom: 0;'>
            Welcome to Your Student Dashboard! 👋
        </h1>
    """, unsafe_allow_html=True)

# Create a centered subheading with minimal top margin
st.markdown("""
    <h3 style='text-align: center; color: #666; margin-top: 0.5rem; margin-bottom: 2rem;'>
        What would you like to do today?
    </h3>
""", unsafe_allow_html=True)

# Navigation buttons for student actions
if st.button('Browse Available Jobs', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/43_Browse_Jobs.py')

if st.button("Update Your Profile",
             type='primary',
             use_container_width=True):
    st.switch_page('pages/45_Update_Profile.py')

if st.button("View and Manage Sublets",
             type='primary',
             use_container_width=True):
    st.switch_page('pages/37_Student_Email_Verification.py')

with col2:
    if st.button('💰 Learn About Cost of Living',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/31_cost_of_living.py')
    
    if st.button("🗺️ View Map",
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/34_student_map.py')

# Add footer space
st.markdown("<br><br>", unsafe_allow_html=True)
