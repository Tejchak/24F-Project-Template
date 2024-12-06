import logging
import streamlit as st
import pandas as pd
import requests

# Set up logging
logger = logging.getLogger(__name__)

# Set page title
st.set_page_config(page_title="Housing Management", layout="wide")

# Title and description
st.title("Housing Management")
st.write("Manage housing records by adding, updating, or deleting them.")

# Fetch zip codes (replace this with your API or database call if needed)
try:
    zip_response = requests.get('http://api:4000/zipcodes')  # Endpoint for fetching zip codes
    zip_response.raise_for_status()
    zip_codes = zip_response.json()  # Assumes the API returns a list of zip codes
except requests.exceptions.HTTPError:
    zip_codes = []
    st.error("Error fetching zip codes. Ensure the API endpoint is correct.")
def fetch_cities():
    response = requests.get('http://api:4000/city')  # Adjust the URL as needed
    if response.status_code == 200:
        return [city['name'] for city in response.json()]  # Extract city names from the response
    else:
        st.error('Error fetching cities from the server: ' + str(response.status_code))
        return []
city_list = fetch_cities()
# Fetch housing records for the user
try:
    response = requests.get('http://api:4000/housing')  # Adjust the endpoint as necessary
    response.raise_for_status()
    housing_records = response.json()

    # Check if there are any housing records
    if not housing_records:
        st.write("You have no housing records.")
    else:
        st.success("Housing records retrieved successfully!")

        # Convert housing records to a DataFrame for better display
        df = pd.DataFrame(housing_records)

        # Display the DataFrame
        st.subheader("Housing Records")
        st.dataframe(df[['Housing_ID', 'Address', 'Rent', 'Sq_Ft', 'City_ID']])  # Display relevant columns
        
        # Section for adding new housing
        st.header("Add New Housing")
        new_city_id = st.selectbox('City:', options=city_list, format_func=lambda x: str(x), key= 'add_housing')
        new_zip_id = st.selectbox("Zip Code", options=zip_codes, format_func=lambda x: str(x))
        new_address = st.text_input("Address")
        new_rent = st.number_input("Rent", min_value=0, step=1)
        new_sq_ft = st.number_input("Square Feet", min_value=1, step=1)

        if st.button("Add Housing"):
            if new_address:
                add_data = {
                    "City_Name": new_city_id,
                    "zipID": new_zip_id,
                    "Address": new_address,
                    "Rent": new_rent,
                    "Sq_Ft": new_sq_ft
                }
                try:
                    response = requests.post('http://api:4000/housing', json=add_data)
                    response.raise_for_status()
                    st.success("Housing added successfully!")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Error adding housing: {e}")
            else:
                st.warning("Please provide a valid address.")

        # Section for updating housing records
        st.header("Update Housing")
        update_housing_id = st.selectbox("Select Housing ID to Update", options=[record['Housing_ID'] for record in housing_records])
        
        # Fetch the selected housing details
        selected_record = next((record for record in housing_records if record['Housing_ID'] == update_housing_id), None)

        if selected_record:
            update_city_id = st.selectbox('City:', options=city_list, format_func=lambda x: str(x), key='update_housing')
            update_zip_id = st.selectbox("New Zip Code", options=zip_codes, index=zip_codes.index(selected_record['zipID']) if selected_record['zipID'] in zip_codes else 0)
            update_address = st.text_input("New Address", value=selected_record['Address'])
            update_rent = st.number_input("New Rent", value=selected_record['Rent'], min_value=0, step=1)
            update_sq_ft = st.number_input("New Square Feet", value=selected_record['Sq_Ft'], min_value=1, step=1)

            if st.button("Update Housing"):
                update_data = {
                    "City_Name": update_city_id,
                    "zipID": update_zip_id,
                    "Address": update_address,
                    "Rent": update_rent,
                    "Sq_Ft": update_sq_ft
                }
                try:
                    response = requests.put(f'http://api:4000/housing/{update_housing_id}', json=update_data)
                    response.raise_for_status()
                    st.success("Housing updated successfully!")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Error updating housing: {e}")

        # Section for deleting housing records
        st.header("Delete Housing")
        delete_housing_id = st.selectbox("Select Housing ID to Delete", options=[record['Housing_ID'] for record in housing_records])

        if st.button("Delete Housing"):
            if delete_housing_id:
                try:
                    response = requests.delete(f'http://api:4000/housing/{delete_housing_id}')
                    response.raise_for_status()
                    st.success("Housing deleted successfully!")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Error deleting housing: {e}")
            else:
                st.warning("Please select a valid Housing ID.")

except requests.exceptions.HTTPError:
    st.write("Error fetching housing records.")

# Optional: Add styling or additional features to enhance the visual appeal
st.markdown("""
<style>
    .stButton > button {
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)
