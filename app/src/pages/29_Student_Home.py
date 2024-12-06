import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

# Welcome the student
if 'first_name' in st.session_state:
    st.title(f"Welcome Student, {st.session_state['first_name']}.")
else:
    st.title("Welcome Student.")

st.write('')
st.write('')
st.write('### What would you like to do today?')

# Navigation buttons for student actions
if st.button('Browse Available Jobs', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/43_Browse_Jobs.py')

if st.button('Apply for a Job', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/44_Apply_Job.py')

if st.button("Update Your Profile",
             type='primary',
             use_container_width=True):
    st.switch_page('pages/45_Update_Profile.py')

if st.button("View and Manage Sublets",
             type='primary',
             use_container_width=True):
    st.switch_page('pages/47_Manage_Sublets.py')
