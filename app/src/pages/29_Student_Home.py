import logging
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

# Welcome message for the student
if 'first_name' in st.session_state:
    st.title(f"Welcome Student, {st.session_state['first_name']}.")
else:
    st.title("Welcome Student.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

# Navigation options for student persona
if st.button('Browse Available Jobs', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/37_Browse_Jobs.py')

if st.button('Apply for a Job', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/38_Apply_Job.py')

if st.button('View Application Status',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/39_View_Applications.py')

if st.button('Get Personalized Recommendations',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/41_Job_Recommendations.py')

if st.button('Update Your Profile',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/42_Update_Profile.py')

if st.button('Delete an Application',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/43_Delete_Application.py')
