import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

st.write("# About CoopConnect")

st.markdown(
    """
    Welcome to CoopConnect - Your Complete Co-op/Internship Planning Platform!

    CoopConnect is a comprehensive solution designed to help Northeastern University students, 
    employers, and parents navigate the co-op experience. Our platform connects all aspects 
    of co-op planning in one place:

    ### For Students
    - Find and compare housing options across different cities
    - Access detailed cost of living data
    - Connect with other students in your target city
    - Browse and apply for co-op positions
    - Find sublet opportunities

    ### For Employers
    - Post co-op positions
    - Access demographic data about student populations
    - Analyze remote work trends
    - View city-specific wage and cost data

    ### For Parents
    - Research safe housing options
    - Access city safety ratings
    - Find nearby hospitals and airports
    - Connect with local communities
    - Plan budgets with accurate cost-of-living data

    ### Key Features
    - Real-time housing market data
    - Safety ratings by neighborhood
    - Cost of living comparisons
    - Student population demographics
    - Healthcare and transportation information
    - Job posting management
    - Sublet coordination

    Built as part of CS 3200 Database Design course at Northeastern University, 
    CoopConnect aims to streamline the co-op experience for all stakeholders involved.
    """
)

# Add a button to switch back to the home page
if st.sidebar.button("Home"):
    st.switch_page("Home.py")
