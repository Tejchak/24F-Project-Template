import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout='wide')

st.title('Moving Information')

st.write("Access all the necessary information for housing and airports to streamline your moving logistics.")

# Section: Housing Information
st.subheader('Housing Information')
try:
    housing_response = requests.get("http://api:4000/housing")  
    if housing_response.status_code == 200:
        housing_data = housing_response.json()
        if housing_data:
            housing_df = pd.DataFrame(housing_data)
            st.dataframe(housing_df, use_container_width=True)
        else:
            st.write("No housing data available.")
    else:
        st.error(f"Failed to fetch housing data: {housing_response.status_code}")
except Exception as e:
    st.error(f"An error occurred while fetching housing information: {e}")

# Section: Airport Information
st.subheader('Airport Information')
try:
    airport_response = requests.get("http://api:4000/airports")  
    if airport_response.status_code == 200:
        airport_data = airport_response.json()
        if airport_data:
            airport_df = pd.DataFrame(airport_data)
            st.dataframe(airport_df, use_container_width=True)
        else:
            st.write("Airport data unavailable.")
    else:
        st.error(f"Failed to retrieve airport data: {airport_response.status_code}")
except Exception as e:
    st.error(f"An error occurred while fetching airport information: {e}")