import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

st.title('City Zip Codes and Student Population')

# Create a dropdown for city selection
city_name = st.selectbox('Select a City:', ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])  # Add more cities as needed

# Add a button to fetch zip codes and student population
if st.button('Get Zip Codes and Student Population'):
    response = requests.get(f'http://api:4000/cities/{city_name}/zipcodes')
    
    if response.status_code == 200:
        data = response.json()
        if data:
            # Display the results in a dataframe
            st.dataframe(data)
        else:
            st.error('No data found for the selected city.')
    else:
        st.error('Error fetching data from the server.')

logger.info(f'User selected city: {city_name}')
  