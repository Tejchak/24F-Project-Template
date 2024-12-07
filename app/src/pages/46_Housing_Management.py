import logging
import streamlit as st
import pandas as pd
import requests
import time

# Set up logging
logger = logging.getLogger(__name__)

# Set page title
st.set_page_config(page_title="Housing Management", layout="wide")

# Custom CSS for sidebar buttons
st.markdown("""
    <style>
        div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
            gap: 0rem;
        }
        .stButton button {
            padding: 0.2rem 1rem;
            font-size: 0.8rem;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; font-size: 144px; color: #4CAF50; margin-top: -70px; margin-left: -20px;'>
        👨‍👩‍👧‍👦
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    if st.button("⬅️ Back", use_container_width=True):
        st.switch_page("pages/40_Parent_Home.py")
    if st.button("🚪 Logout", use_container_width=True):
        # Clear session state
        for key in st.session_state.keys():
            del st.session_state[key]
        # Redirect to home page
        st.switch_page("Home.py")
    st.divider()

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
        # Show success message that will disappear after 3 seconds
        success_container = st.empty()
        success_container.success("Housing records retrieved successfully!")
        time.sleep(3)
        success_container.empty()

        # Convert housing records to a DataFrame for better display
        df = pd.DataFrame(housing_records)

        # Create tabs for different operations
        view_tab, add_tab, update_tab, delete_tab = st.tabs(["View Housing", "Add Housing", "Update Housing", "Delete Housing"])

        # View Housing Tab
        with view_tab:
            st.subheader("Housing Records")
            st.markdown("""
                Here you can view all available housing records. The table shows:
                - **Housing ID**: Unique identifier for each property
                - **Address**: Full property address
                - **Rent**: Monthly rental cost
                - **Square Feet**: Property size
                - **City ID**: Location identifier
                
                💡 _Tip: Click on column headers to sort the data_
            """)
            st.dataframe(df[['Housing_ID', 'Address', 'Rent', 'Sq_Ft', 'City_ID']])

        # Add Housing Tab
        with add_tab:
            st.subheader("Add New Housing")
            st.markdown("""
                Add a new housing property to the database. All fields are required.
                
                📝 **Instructions**:
                1. Select the city from the dropdown
                2. Choose the appropriate ZIP code
                3. Enter the complete property address
                4. Specify the monthly rent
                5. Input the total square footage
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                new_city_id = st.selectbox('City:', options=city_list, format_func=lambda x: str(x), key='add_housing')
                new_zip_id = st.selectbox("Zip Code:", options=zip_codes, format_func=lambda x: str(x))
                new_address = st.text_input("Property Address:", placeholder="Enter complete address")
            with col2:
                new_rent = st.number_input("Monthly Rent ($):", min_value=0, step=100)
                new_sq_ft = st.number_input("Square Footage:", min_value=1, step=50)

            if st.button("Add Housing", type="primary"):
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
                        time.sleep(1)
                        st.rerun()
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Error adding housing: {e}")
                else:
                    st.warning("Please provide a valid address.")

        # Update Housing Tab
        with update_tab:
            st.subheader("Update Existing Housing")
            st.markdown("""
                Modify details of an existing housing property.
                
                📝 **Steps to update**:
                1. Select the Housing ID you want to update
                2. Modify any of the fields below
                3. Click 'Update Housing' to save changes
                
                ⚠️ _Note: All fields must be filled, even if you're only updating one field_
            """)
            
            update_housing_id = st.selectbox(
                "Select Housing ID to Update:", 
                options=[record['Housing_ID'] for record in housing_records],
                help="Choose the ID of the property you want to modify"
            )
            
            selected_record = next((record for record in housing_records if record['Housing_ID'] == update_housing_id), None)

            if selected_record:
                col1, col2 = st.columns(2)
                with col1:
                    update_city_id = st.selectbox('City:', options=city_list, format_func=lambda x: str(x), key='update_housing')
                    update_zip_id = st.selectbox(
                        "New Zip Code:", 
                        options=zip_codes, 
                        index=zip_codes.index(selected_record['zipID']) if selected_record['zipID'] in zip_codes else 0
                    )
                    update_address = st.text_input("New Address:", value=selected_record['Address'])
                with col2:
                    update_rent = st.number_input("New Monthly Rent ($):", value=selected_record['Rent'], min_value=0, step=100)
                    update_sq_ft = st.number_input("New Square Footage:", value=selected_record['Sq_Ft'], min_value=1, step=50)

                if st.button("Update Housing", type="primary"):
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
                        time.sleep(1)
                        st.rerun()
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Error updating housing: {e}")

        # Delete Housing Tab
        with delete_tab:
            st.subheader("Delete Housing")
            st.markdown("""
                ⚠️ **Warning**: This action cannot be undone!
                
                To delete a housing record:
                1. Select the Housing ID from the dropdown
                2. Confirm that it's the correct property
                3. Click 'Delete Housing' to permanently remove the record
            """)
            
            delete_housing_id = st.selectbox(
                "Select Housing ID to Delete:", 
                options=[record['Housing_ID'] for record in housing_records],
                help="Choose the ID of the property you want to remove"
            )
            
            # Show property details before deletion
            if delete_housing_id:
                property_to_delete = next((record for record in housing_records if record['Housing_ID'] == delete_housing_id), None)
                if property_to_delete:
                    st.info(f"""
                        **Property Details**:
                        - Address: {property_to_delete['Address']}
                        - Rent: ${property_to_delete['Rent']}
                        - Square Feet: {property_to_delete['Sq_Ft']}
                    """)

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Delete Housing", type="primary"):
                    if delete_housing_id:
                        try:
                            response = requests.delete(f'http://api:4000/housing/{delete_housing_id}')
                            response.raise_for_status()
                            st.success("Housing deleted successfully!")
                            time.sleep(1)
                            st.rerun()
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
