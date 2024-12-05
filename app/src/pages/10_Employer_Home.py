import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Employer, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Find Best Locations to Set Up CO-OP', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/11_Population_Per_Zip.py')

if st.button('Create a new job posting', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/12_Create_Job_Posting.py')

if st.button("Job Postings Management",
             type='primary',
             use_container_width=True):
  st.switch_page('pages/13_Job_Postings_Management.py')