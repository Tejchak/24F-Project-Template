import logging
logger = logging.getLogger(__name__)
import streamlit as st
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import requests

# Set page title
st.set_page_config(page_title="Employer Job Postings Management", layout="wide")

SideBarLinks()

# Title and description
st.title("Employer Job Postings Management")
st.write("Manage job postings by searching for a user, updating postings, or deleting them.")

# Section for searching job postings
st.header("Search Job Postings")
user_email = st.text_input("Enter User Email", placeholder="user@example.com")

if st.button("Search"):
    if user_email:
        try:
            response = requests.get(f'http://api:4000/users/email/{user_email}/job_postings')
            response.raise_for_status()
            job_postings = response.json()
            st.success("Job postings retrieved successfully!")

            # Convert job postings to a DataFrame for better display
            df = pd.DataFrame(job_postings)

            # Convert Location_ID to string and remove commas
            df['Location_ID'] = df['Location_ID'].astype(str).str.replace(',', '')

            # Sort the DataFrame by Compensation in descending order
            df_sorted = df.sort_values(by='Compensation', ascending=False)

            # Display the DataFrame without highlighting
            st.subheader("Job Postings")
            st.dataframe(df_sorted)  # Display sorted DataFrame

            # Create a collapsible section for each job posting
            for posting in job_postings:
                with st.expander(f"Job Posting ID: {posting['Post_ID']}"):
                    st.markdown(f"**Compensation:** ${posting['Compensation']}")
                    st.markdown(f"**Location (ZIP Code):** {str(posting['Location_ID']).replace(',', '')}")  # Remove commas
                    st.markdown(f"**User ID:** {posting['User_ID']}")

        except requests.exceptions.HTTPError as e:
            st.error(f"Error fetching job postings: {e}")
    else:
        st.warning("Please enter a valid email.")

# Section for updating job postings
st.header("Update Job Posting")
post_id = st.number_input("Enter Job Posting ID to Update", min_value=1)
new_compensation = st.number_input("New Compensation", min_value=0)

# Fetch available ZIP codes
try:
    response = requests.get('http://api:4000/zipcodes')
    response.raise_for_status()
    zipcodes = response.json()
except requests.exceptions.HTTPError as e:
    st.error(f"Error fetching zip codes: {e}")
    zipcodes = []

# Use selectbox for ZIP code selection
new_location_id = st.selectbox("Select New Location (ZIP Code)", options=zipcodes)

if st.button("Update Job Posting"):
    if post_id and (new_compensation or new_location_id):
        update_data = {
            "compensation": new_compensation if new_compensation else None,
            "location_id": new_location_id if new_location_id else None  # Use the selected ZIP code
        }
        try:
            response = requests.put(f'http://api:4000/job_postings/{post_id}', json=update_data)
            response.raise_for_status()
            st.success("Job posting updated successfully!")
        except requests.exceptions.HTTPError as e:
            st.error(f"Error updating job posting: {e}")
    else:
        st.warning("Please provide a valid Job Posting ID and at least one field to update.")

# Section for deleting job postings
st.header("Delete Job Posting")
delete_post_id = st.number_input("Enter Job Posting ID to Delete", min_value=1)

if st.button("Delete Job Posting"):
    if delete_post_id:
        try:
            response = requests.delete(f'http://api:4000/job_postings/{delete_post_id}')
            response.raise_for_status()
            st.success("Job posting deleted successfully!")
        except requests.exceptions.HTTPError as e:
            st.error(f"Error deleting job posting: {e}")
    else:
        st.warning("Please enter a valid Job Posting ID.")

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