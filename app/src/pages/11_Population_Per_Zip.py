import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

st.title('City Zip Codes and Student Population')

def fetch_cities():
    response = requests.get('http://api:4000/city')  # Adjust the URL as needed
    if response.status_code == 200:
        return [city['name'] for city in response.json()]  # Extract city names from the response
    else:
        st.error('Error fetching cities from the server: ' + str(response.status_code))
        return []

# Fetch the list of cities
city_list = fetch_cities()

# Create a dropdown for city selection
city_name = st.selectbox('Select a City:', city_list)


# Add a button to fetch zip codes and student population
if st.button('Get Zip Codes and Student Population'):
    response = requests.get(f'http://api:4000/cities/{city_name}/student_population')
    
    # Print the response text for debugging
    print("Response Text:", response.text)
    try:
        data = response.json()  # Attempt to parse the response as JSON
    except ValueError as e:
        data = None
        print("Error parsing JSON response:", response.text)
    
    if data:
        st.dataframe(data)
    else:
        if response.text == "No zipcodes for selected city":
            st.write("No zipcodes for selected city")
        else:
            st.error('No data found for the selected city.')

logger.info(f'User selected city: {city_name}')
  