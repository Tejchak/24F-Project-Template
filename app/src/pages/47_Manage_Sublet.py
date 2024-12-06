import streamlit as st
import requests
import pandas as pd

# Backend API base URL
API_BASE_URL = "http://api:4000"  # Replace with your backend's base URL

# Set page configuration
st.set_page_config(layout='wide')

# Page title
st.title("View and Manage Sublets")

# Check if user ID is in session state
if 'user_id' not in st.session_state:
    st.error("You need to verify your email first.")
    st.stop()

user_id = st.session_state.user_id  # Get the user ID from session state

# Function to fetch all sublets
def fetch_all_sublets():
    try:
        response = requests.get(f"{API_BASE_URL}/sublets")  # Fetch all sublets
        response.raise_for_status()
        return response.json()  # Return sublet data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sublets: {e}")
        return []

# Function to fetch all housing IDs
def fetch_housing_ids():
    try:
        response = requests.get(f"{API_BASE_URL}/housing")  # Adjust endpoint to fetch housing IDs
        response.raise_for_status()
        return response.json()  # Return housing data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching housing IDs: {e}")
        return []

# Function to fetch sublets for the user
def fetch_user_sublets():
    try:
        response = requests.get(f"{API_BASE_URL}/students/{user_id}/sublets")  # Fetch user's sublets
        response.raise_for_status()
        return response.json()  # Return user sublet data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching user sublets: {e}")
        return []

# Function to create a new sublet
def create_sublet(housing_id, start_date, end_date):
    try:
        payload = {
            "Housing_ID": housing_id,
            "Subleter_ID": user_id,  # Set Subleter_ID to the user's ID
            "Start_Date": str(start_date),
            "End_Date": str(end_date),
        }
        response = requests.post(f"{API_BASE_URL}/students/{user_id}/sublet", json=payload)
        if response.status_code == 201:
            st.success("Sublet created successfully!")
        else:
            st.error(f"Failed to create sublet: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating sublet: {e}")

# Function to update a sublet
def update_sublet(sublet_id, housing_id, start_date, end_date):
    try:
        payload = {
            "Housing_ID": housing_id,
            "Start_Date": str(start_date),
            "End_Date": str(end_date),
        }
        response = requests.put(f"{API_BASE_URL}/sublets/{sublet_id}", json=payload)
        if response.status_code == 200:
            st.success("Sublet updated successfully!")
        else:
            st.error(f"Failed to update sublet: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating sublet: {e}")

# Function to delete a sublet
def delete_sublet(sublet_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/sublets/{sublet_id}")
        if response.status_code == 200:
            st.success("Sublet deleted successfully!")
        else:
            st.error(f"Failed to delete sublet: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting sublet: {e}")

# Fetch all sublets and housing IDs
all_sublets = fetch_all_sublets()
housing_ids = fetch_housing_ids()
user_sublets = fetch_user_sublets()  # Fetch user's sublets

# Display all sublets
if all_sublets:
    st.write("### All Sublets")
    all_sublet_df = pd.DataFrame(all_sublets)
    if not all_sublet_df.empty:
        all_sublet_df = all_sublet_df.rename(
            columns={
                'Start_Date': 'Start Date',
                'End_Date': 'End Date',
                'Sublet_ID': 'Sublet ID',
                'Subleter_ID': 'Subleter ID',
                'Housing_ID': 'Housing ID',
            }
        )
        all_sublet_df = all_sublet_df[['Start Date', 'End Date', 'Housing ID', 'Sublet ID', 'Subleter ID']]
        st.dataframe(all_sublet_df, use_container_width=True)
    else:
        st.write("No sublets available.")
else:
    st.warning("No sublets found.")

# Sublet Management Options
st.write("### Manage Sublets")

# Create a new sublet
with st.expander("Create a New Sublet"):
    housing_id = st.selectbox("Select Housing ID", options=[h['Housing_ID'] for h in housing_ids])  # Dropdown for housing IDs
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    if st.button("Create Sublet"):
        if housing_id and start_date and end_date:
            create_sublet(housing_id, start_date, end_date)
        else:
            st.error("Please fill out all fields.")

# Update an existing sublet
with st.expander("Update an Existing Sublet"):
    if user_sublets:
        sublet_id_to_update = st.selectbox("Select Sublet ID to Update", options=[sublet['Sublet_ID'] for sublet in user_sublets], key='sublet update')  # Dropdown for user sublet IDs
        housing_id = st.selectbox("Select Housing ID", options=[h['Housing_ID'] for h in housing_ids], key='housing update')  # Dropdown for housing IDs
        start_date = st.date_input("New Start Date", key="update_start_date")
        end_date = st.date_input("New End Date", key="update_end_date")
        if st.button("Update Sublet"):
            if sublet_id_to_update and housing_id and start_date and end_date:
                update_sublet(sublet_id_to_update, housing_id, start_date, end_date)
            else:
                st.error("Please fill out all fields.")
    else:
        st.write("You have no sublets to update.")

# Delete a sublet
with st.expander("Delete a Sublet"):
    if user_sublets:
        sublet_id_to_delete = st.selectbox("Select Sublet ID to Delete", options=[sublet['Sublet_ID'] for sublet in user_sublets])  # Dropdown for user sublet IDs
        if st.button("Delete Sublet"):
            if sublet_id_to_delete:
                delete_sublet(sublet_id_to_delete)
            else:
                st.error("Please provide a valid Sublet ID.")
    else:
        st.write("You have no sublets to delete.")

# Add a logout button in the sidebar
st.sidebar.header('Actions')
if st.sidebar.button('Logout'):
    st.session_state.clear()  # Clear session state on logout
    st.switch_page('Home.py')  # Refresh the app to go back to the homepage