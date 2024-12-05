import logging
logger = logging.getLogger(__name__)
import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
import requests
from modules.nav import SideBarLinks

# Initialize the sidebar links
SideBarLinks()

# Set up the page
st.markdown("# Zipcode and Location Analysis")
st.sidebar.header("Location Analysis")
st.write(
    """This map shows location information including safety ratings, student population,
    and housing information across different zipcodes."""
)

# Function to fetch location data from the API
@st.cache_data
def get_location_data():
    try:
        # Get city data
        cities_response = requests.get('http://api:4000/city').json()
        
        # Get housing data
        housing_response = requests.get('http://api:4000/housing').json()
        
        # Create a DataFrame with the combined data
        locations_data = []
        
        for city in cities_response:
            city_id = city['city_id']
            city_name = city['name']
            
            # Filter housing data for this city
            city_housing = [h for h in housing_response if h[1] == city_id]
            
            for house in city_housing:
                locations_data.append({
                    'city': city_name,
                    'zipcode': house[2],
                    'address': house[3],
                    'rent': house[4],
                    'sqft': house[5],
                    'lat': 40.7128 + (hash(str(house[2])) % 100) / 1000,  # Random but consistent lat
                    'lon': -74.0060 + (hash(str(house[3])) % 100) / 1000  # Random but consistent lon
                })
        
        return pd.DataFrame(locations_data)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

# Get the data
try:
    df = get_location_data()
    
    if not df.empty:
        # Create layers for the map
        ALL_LAYERS = {
            "Housing Locations": pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius="sqft",
                radius_scale=0.01,
                pickable=True,
            ),
            "Rent Heatmap": pdk.Layer(
                "HexagonLayer",
                data=df,
                get_position=["lon", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                get_elevation="rent",
                pickable=True,
                extruded=True,
            ),
        }

        # Create layer selector in sidebar
        st.sidebar.markdown("### Map Layers")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)
        ]

        # Create the map
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state={
                        "latitude": df['lat'].mean(),
                        "longitude": df['lon'].mean(),
                        "zoom": 11,
                        "pitch": 50,
                    },
                    layers=selected_layers,
                    tooltip={
                        "html": "<b>Address:</b> {address}<br/>"
                                "<b>Rent:</b> ${rent}<br/>"
                                "<b>Square Feet:</b> {sqft}<br/>"
                                "<b>Zipcode:</b> {zipcode}",
                        "style": {
                            "backgroundColor": "steelblue",
                            "color": "white"
                        }
                    }
                )
            )

            # Display data table below map
            st.subheader("Location Details")
            st.dataframe(
                df[['city', 'zipcode', 'address', 'rent', 'sqft']],
                hide_index=True
            )
        else:
            st.error("Please choose at least one layer above.")
    else:
        st.error("No data available to display.")

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )