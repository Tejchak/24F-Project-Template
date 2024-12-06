##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout = 'wide')

# If a user is at this page, we assume they are not 
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false. 
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel. 
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

# set the title of the page and provide a simple prompt. 
logger.info("Loading the Home page of the app")
st.title('Welcome to Coop Connect 🎓')
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 2rem; border-radius: 10px; margin: 1rem 0;'>
        <h3>Your Gateway to Professional Opportunities</h3>
        <p>Coop Connect brings together students, employers, and families in a seamless platform 
        for managing cooperative education experiences. Whether you're seeking talent, 
        exploring opportunities, or supporting a student's journey, we're here to help.</p>
    </div>
""", unsafe_allow_html=True)

# Login Section
st.write('### Choose Your Role to Get Started')

# Create two columns for better layout
col1, col2 = st.columns(2)

with col1:
    
    if st.button('🎓 Login as Sarah (Student)', 
                type='primary', 
                use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'student'
        st.session_state['first_name'] = 'Sarah'
        logger.info('Logging in as Student Persona')
        st.switch_page('pages/29_Student_Home.py')
    
    if st.button('💼 Login as Edward (Employer)', 
                type='primary', 
                use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'employer'
        st.session_state['first_name'] = 'Edward'
        st.switch_page('pages/10_Employer_Home.py')

with col2:
    
    if st.button('👨‍👩‍👧‍👦 Login as Helen (Parent)', 
                type='primary', 
                use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'parent'
        st.session_state['first_name'] = 'Helen'
        logger.info('Logging in as Parent Persona')
        st.switch_page('pages/40_Parent_Home.py')

    if st.button('⚙️ Login as John (System Admin)', 
                type='primary', 
                use_container_width=True):
        st.switch_page('pages/33_Login_System_Admin.py')

# Add footer with additional information
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-top: 2rem; text-align: center;'>
        <p><small>Coop Connect is Northeastern University's premier platform for cooperative education management.
        For technical support, please contact the system administrator.</small></p>
    </div>
""", unsafe_allow_html=True)
