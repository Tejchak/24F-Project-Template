import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title('Parent Home Page')

#Access cost of living prices for cities
if st.button('Learn about cost of living',
             type='primary',
             use_container_width=True):
    st.swtich_page('pages/31_cost_of_living.py')
    
#Access moving information
if st.button('Moving Information',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/41_Moving_Info.py')
    

#Access safety information for a specific city


