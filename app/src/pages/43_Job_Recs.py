import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout='wide')

st.title('Safety Information')

# Input for City_ID
city_id = st.text_input('Enter City_ID:', '')

if city_id:
    # Gets Safety rating of a city
    st.subheader('Safety Rating')
    try:
        safety_response = requests.get(f"http://api:4000/location/safety/{city_id}")  
        if safety_response.status_code == 200:
            safety_data = safety_response.json()
            st.write(f"Safety Rating for City_ID {city_id}: {safety_data.get('Safety_Rating', 'Unknown')}")
        elif safety_response.status_code == 404:
            st.warning(f"No safety information found for City_ID {city_id}.")
        else:
            st.error(f"Error fetching safety information: {safety_response.status_code}")
    except Exception as e:
        st.error(f"An error occurred while fetching safety information: {e}")

    # Gets hospitals that match with the city_id
    st.subheader('Nearby Hospitals')
    try:
        hospitals_response = requests.get(f"http://api:4000/hospitals/{city_id}")  
        if hospitals_response.status_code == 200:
            hospitals_data = hospitals_response.json()
            hospitals_df = pd.DataFrame(hospitals_data)
            st.dataframe(hospitals_df, use_container_width=True)
        elif hospitals_response.status_code == 404:
            st.warning(f"No hospitals found for City_ID {city_id}.")
        else:
            st.error(f"Error fetching hospital information: {hospitals_response.status_code}")
    except Exception as e:
        st.error(f"An error occurred while fetching hospital information: {e}")