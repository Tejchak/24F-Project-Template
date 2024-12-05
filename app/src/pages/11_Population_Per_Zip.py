import logging
import requests
import streamlit as st

# Set up logging
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(layout='wide')

# Title of the page
st.title('Employer City Info')

# Function to fetch cities
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
if st.button('Get City Info'):
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

    # Fetch and display average wage and proportion of hybrid workers only when the button is pressed
    try:
        wage_response = requests.get(f'http://api:4000/cities/{city_name}/wage_hybrid')
        wage_response.raise_for_status()
        wage_data = wage_response.json()

        # Display the data
        st.subheader(f"City: {city_name}")
        st.write(f"Average Wage: ${wage_data['Average_Wage']}")
        st.write(f"Proportion of Hybrid Workers: {float(wage_data['Proportion_Hybrid_Workers']) * 100:.2f}%")
        
    except requests.exceptions.RequestException as e:
        st.error(f'Error fetching wage and hybrid worker data: {e}')

logger.info(f'User selected city: {city_name}')
  