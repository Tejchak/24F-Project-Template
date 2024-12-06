import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; font-size: 144px; color: #4CAF50; margin-top: -70px; margin-left: -20px;'>
        👨‍👩‍👧‍👦
    </div>
    """, unsafe_allow_html=True)
    
    st.title("Navigation")
    
    # Back button
    if st.button("⬅️ Back"):
        st.switch_page("Home.py")  # Changed from pages/29_Student_Home.py
    
    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("Home.py")
    
    st.divider()

# Create a clean header section with custom styling
if 'first_name' in st.session_state:
    st.markdown(f"""
        <h1 style='text-align: center; color: #1E3D59; padding-top: 1rem; padding-bottom: 0; margin-bottom: 0;'>
            Welcome, {st.session_state['first_name']}!
        </h1>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <h1 style='text-align: center; color: #1E3D59; padding-top: 1rem; padding-bottom: 0; margin-bottom: 0;'>
            Welcome to Your Parent Dashboard! 👋
        </h1>
    """, unsafe_allow_html=True)

# Create a centered subheading with minimal top margin
st.markdown("""
    <h3 style='text-align: center; color: #666; margin-top: 0.5rem; margin-bottom: 2rem;'>
        What would you like to explore today?
    </h3>
""", unsafe_allow_html=True)

# Create two columns for better button layout
col1, col2 = st.columns(2, gap="large")

with col1:
    if st.button('💰 Cost of Living Information',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/31_cost_of_living.py')
    
    if st.button('🏠 Housing Management',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/46_Housing_Management.py')

with col2:
    if st.button('🚚 Moving Information',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/41_Moving_Info.py')
    
    if st.button('🛡️ Safety Information',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/42_Safety_Info.py')

# Add footer space
st.markdown("<br><br>", unsafe_allow_html=True)

