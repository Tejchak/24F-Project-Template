import logging
import requests
import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

st.title('Create a New Job Posting')
 #Fetch zip codes from the API
try:
    response = requests.get('http://api:4000/zipcodes')
    response.raise_for_status()
    zipcodes = response.json()  # Get the list of zip codes
except requests.exceptions.RequestException as e:
    st.error(f'Error fetching zip codes: {e}')
    zipcodes = []
# Form for creating a new job posting
with st.form(key='job_posting_form'):
    compensation = st.number_input('Compensation (in dollars)', min_value=0, step=1000)
    location_id = st.selectbox('Location ID', zipcodes)
    user_email = st.text_input('User Email')

    submit_button = st.form_submit_button(label='Create Job Posting')


if submit_button:
    # Prepare the data for the POST request
    job_data = {
        'compensation': compensation,
        'location_id': location_id,
        'user_email': user_email
    }

    # Make the POST request to create a new job posting
    try:
        response = requests.post('http://api:4000/job_postings', json=job_data)
        response.raise_for_status()  # Raise an error for bad responses

        # Display success message
        st.success('Job posting created successfully!')
    except requests.exceptions.RequestException as e:
        st.write(f'Error creating job posting, could not find email in database')
