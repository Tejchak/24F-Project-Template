import logging
import requests
import streamlit as st
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(layout='wide')

# Title of the page
st.title('City Information: Hospitals and Safety Ratings')

# Function to fetch cities
def fetch_cities():
    response = requests.get('http://api:4000/city')  # Adjust the URL as needed
    if response.status_code == 200:
        return [city['name'] for city in response.json()]  # Extract city names from the response
    else:
        st.error('Error fetching cities from the server: ' + str(response.status_code))
        return []

# Sidebar for city selection
st.sidebar.header('Select a City')
city_list = fetch_cities()
city_name = st.sidebar.selectbox('City:', city_list)

# Add a button to fetch hospitals and safety ratings for the selected city
if st.sidebar.button('Get City Info'):
    # Fetch hospitals for the selected city
    response = requests.get(f'http://api:4000/hospitals/{city_name}')
    
    try:
        hospital_data = response.json()  # Attempt to parse the response as JSON
    except ValueError as e:
        hospital_data = None
        st.error("Error parsing JSON response: " + str(e))
    
    if hospital_data:
        # Display the hospital data
        st.subheader(f"Hospitals in {city_name}")
        st.dataframe(hospital_data)
    else:
        if response.status_code == 404:
            st.write("No hospitals found for the selected city.")
        else:
            st.error('Error fetching hospital data.')

    # Fetch safety ratings for each ZIP code in the selected city
    try:
        safety_response = requests.get(f'http://api:4000/cities/{city_name}/safety_rating')
        safety_response.raise_for_status()
        safety_data = safety_response.json()

        # Display the safety ratings
        st.subheader(f"Safety Ratings for ZIP Codes in {city_name}")
        if safety_data:
            # Create a DataFrame and reorder columns
            safety_df = pd.DataFrame(safety_data)
            safety_df = safety_df[['Zip', 'Safety_Rating']]  # Ensure ZIP comes before Safety Rating
            st.dataframe(safety_df)
        else:
            st.write("No safety ratings found for the specified city.")
        
    except requests.exceptions.RequestException as e:
        st.error(f'Error fetching safety ratings: {e}')

logger.info(f'User selected city: {city_name}')

# Add a logout button in the sidebar
if st.sidebar.button('Logout'):
    st.switch_page('Home.py')# Refresh the app to go back to the homepage