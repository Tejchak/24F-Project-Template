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
st.write("Manage job postings by browsing through your postings, updating postings, or deleting them.")

# Check if user ID is in session state
if 'user_id' in st.session_state:
    user_id = st.session_state.user_id
    st.write(f"Welcome! Your User ID is: {user_id}")

    # Fetch job postings for the user
    try:
        response = requests.get(f'http://api:4000/users/{user_id}/job_postings')
        response.raise_for_status()
        job_postings = response.json()

        # Check if there are any job postings
        if not job_postings:
            st.write("You have no postings for this ID.")
        else:
            st.success("Job postings retrieved successfully!")

            # Convert job postings to a DataFrame for better display
            df = pd.DataFrame(job_postings)

            # Sort the DataFrame by Compensation in descending order
            df_sorted = df.sort_values(by='Compensation', ascending=False)

            # Display the DataFrame without the Bio column
            st.subheader("Job Postings")
            st.dataframe(df_sorted[['Title', 'Compensation', 'Location_ID', 'Post_ID', 'User_ID']])  # Display relevant columns

            # Create a collapsible section for each job posting
            for posting in job_postings:
                with st.expander(f"Job Posting ID: {posting['Post_ID']}"):
                    st.markdown(f"**Title:** {posting['Title']}")
                    st.markdown(f"**Compensation:** ${posting['Compensation']}")
                    st.markdown(f"**Location (ZIP Code):** {posting['Location_ID']}")
                    st.markdown(f"**User ID:** {posting['User_ID']}")
                    st.markdown(f"**Description:** {posting['Bio']}")  # Include Bio in the dropdown

            # Fetch all available ZIP codes from the database
            try:
                zip_response = requests.get('http://api:4000/zipcodes')  # Adjust the endpoint as necessary
                zip_response.raise_for_status()
                zip_codes = zip_response.json()
            except requests.exceptions.HTTPError:
                st.error("Error fetching ZIP codes.")
                zip_codes = []  # Fallback to an empty list if there's an error

            # Section for updating job postings
            st.header("Update Job Posting")
            post_id = st.selectbox("Select Job Posting ID to Update", options=[posting['Post_ID'] for posting in job_postings])
            
            # Fetch the selected posting details
            selected_posting = next((posting for posting in job_postings if posting['Post_ID'] == post_id), None)

            if selected_posting:
                new_title = st.text_input("New Title", value="Inter")  # Default title
                new_bio = st.text_area("New Description", value="Collaborate")  # Default description
                new_compensation = st.number_input("New Compensation", min_value=0, value=selected_posting['Compensation'])  # Default compensation
                new_location_id = st.selectbox("Select New Location (ZIP Code)", options=zip_codes)  # Use all ZIP codes

                if st.button("Update Job Posting"):
                    if post_id and (new_title or new_bio or new_compensation or new_location_id):
                        update_data = {
                            "title": new_title,
                            "bio": new_bio,
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
            delete_post_id = st.selectbox("Select Job Posting ID to Delete", options=[posting['Post_ID'] for posting in job_postings])

            if st.button("Delete Job Posting"):
                if delete_post_id:
                    try:
                        response = requests.delete(f'http://api:4000/job_postings/{delete_post_id}')
                        response.raise_for_status()
                        st.success("Job posting deleted successfully!")
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Error deleting job posting: {e}")
                else:
                    st.warning("Please select a valid Job Posting ID.")

    except requests.exceptions.HTTPError:
        st.write("You have no postings for this ID.")

else:
    st.error("You need to verify your email first.")

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