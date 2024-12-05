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

# Add this dictionary at the top of the file, after imports
CITY_COORDINATES = {
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Boston': {'lat': 42.3601, 'lon': -71.0589},
    'San Francisco': {'lat': 37.7749, 'lon': -122.4194},
    'Seattle': {'lat': 47.6062, 'lon': -122.3321},
    'Miami': {'lat': 25.7617, 'lon': -80.1918},
    'Detroit': {'lat': 42.3314, 'lon': -83.0458},
    'Houston': {'lat': 29.7604, 'lon': -95.3698},
    'Atlanta': {'lat': 33.7490, 'lon': -84.3880}
}

# Function to fetch cities
def fetch_cities():
    try:
        response = requests.get('http://api:4000/city')
        if response.status_code == 200:
            return [city['name'] for city in response.json()]
        return []
    except Exception as e:
        st.error(f"Error fetching cities: {str(e)}")
        return []

# Function to fetch location data for a specific city
@st.cache_data
def get_location_data(selected_city):
    try:
        # Get city data
        cities_response = requests.get('http://api:4000/city').json()
        
        # Get housing data
        housing_response = requests.get('http://api:4000/housing').json()
        
        # Find the city_id for the selected city
        city_id = None
        city_data = None
        for city in cities_response:
            if city['name'] == selected_city:
                city_id = city['city_id']
                city_data = city
                break
        
        if not city_id:
            return pd.DataFrame()
        
        # Filter housing data for the selected city
        locations_data = []
        city_housing = [h for h in housing_response if h['City_ID'] == city_id]
        
        for house in city_housing:
            base_coords = CITY_COORDINATES.get(selected_city, {'lat': 0, 'lon': 0})
            locations_data.append({
                'city': selected_city,
                'zipcode': house['zipID'],
                'address': house['Address'],
                'rent': house['Rent'],
                'sqft': house['Sq_Ft'],
                'lat': base_coords['lat'] + (hash(str(house['zipID'])) % 10) / 1000,
                'lon': base_coords['lon'] + (hash(str(house['Address'])) % 10) / 1000
            })
        
        return pd.DataFrame(locations_data)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        logger.error(f"Data fetch error: {str(e)}")
        return pd.DataFrame()

# Get list of cities and create selector
cities = fetch_cities()
selected_city = st.sidebar.selectbox("Select a City", cities)

# Get the data for selected city
try:
    df = get_location_data(selected_city)
    
    if not df.empty:
        # Create layers for the map with adjusted parameters
        ALL_LAYERS = {
            "Housing Locations": pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius=50,  # Smaller radius for more precise markers
                pickable=True,
            ),
            "Rent Heatmap": pdk.Layer(
                "HexagonLayer",
                data=df,
                get_position=["lon", "lat"],
                radius=100,  # Smaller radius for more detailed heatmap
                elevation_scale=2,  # Adjust elevation scale for better visualization
                elevation_range=[0, 500],  # Adjust elevation range
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
                        "zoom": 12,  # Adjust zoom level for better focus
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
            st.subheader(f"Location Details for {selected_city}")
            st.dataframe(
                df[['city', 'zipcode', 'address', 'rent', 'sqft']],
                hide_index=True
            )
        else:
            st.error("Please choose at least one layer above.")
    else:
        st.error(f"No data available for {selected_city}")
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )