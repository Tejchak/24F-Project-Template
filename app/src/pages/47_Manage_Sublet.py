import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Backend API base URL
API_BASE_URL = "http://localhost:4000"  # Replace with your backend's base URL

# Set page configuration
st.set_page_config(layout='wide')

# Page title
st.title("View and Manage Sublets")

# Ensure user is logged in and their ID is in the session
if 'user_id' not in st.session_state:
    st.error("You must be logged in to manage sublets.")
    st.stop()

# Function to fetch sublets for the user
def fetch_sublets(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/students/{user_id}/sublets")
        response.raise_for_status()
        return response.json()  # Return sublet data as a JSON object
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sublets: {e}")
        return []

# Function to create a new sublet
def create_sublet(user_id, housing_id, start_date, end_date):
    try:
        payload = {
            "Housing_ID": housing_id,
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
def update_sublet(sublet_id, title, description, rent, address, start_date, end_date):
    try:
        payload = {
            "title": title,
            "description": description,
            "rent": rent,
            "address": address,
            "start_date": str(start_date),
            "end_date": str(end_date),
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

# Fetch and display the user's sublets
user_id = st.session_state['user_id']
sublets = fetch_sublets(user_id)

if sublets:
    st.write("### Your Sublets")
    sublet_df = pd.DataFrame(sublets)
    if not sublet_df.empty:
        sublet_df = sublet_df.rename(
            columns={
                'Sublet_ID': 'Sublet ID',
                'Housing_ID': 'Housing ID',
                'Start_Date': 'Start Date',
                'End_Date': 'End Date',
            }
        )
        st.dataframe(sublet_df, use_container_width=True)
    else:
        st.write("No sublets available.")
else:
    st.warning("You currently have no sublets.")

# Sublet Management Options
st.write("### Manage Sublets")

# Create a new sublet
with st.expander("Create a New Sublet"):
    housing_id = st.text_input("Housing ID")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    if st.button("Create Sublet"):
        if housing_id and start_date and end_date:
            create_sublet(user_id, housing_id, start_date, end_date)
        else:
            st.error("Please fill out all fields.")

# Update an existing sublet
with st.expander("Update an Existing Sublet"):
    sublet_id = st.text_input("Sublet ID to Update")
    title = st.text_input("Title")
    description = st.text_area("Description")
    rent = st.number_input("Rent", min_value=0)
    address = st.text_input("Address")
    start_date = st.date_input("Start Date", key="update_start_date")
    end_date = st.date_input("End Date", key="update_end_date")
    if st.button("Update Sublet"):
        if sublet_id and title and description and rent and address and start_date and end_date:
            update_sublet(sublet_id, title, description, rent, address, start_date, end_date)
        else:
            st.error("Please fill out all fields.")

# Delete a sublet
with st.expander("Delete a Sublet"):
    sublet_id_to_delete = st.text_input("Sublet ID to Delete")
    if st.button("Delete Sublet"):
        if sublet_id_to_delete:
            delete_sublet(sublet_id_to_delete)
        else:
            st.error("Please provide a valid Sublet ID.")

# Add a logout button in the sidebar
st.sidebar.header('Actions')
if st.sidebar.button('Logout'):
    st.session_state.clear()  # Clear session state on logout
    st.experimental_rerun()  # Refresh the app to go back to the homepage
