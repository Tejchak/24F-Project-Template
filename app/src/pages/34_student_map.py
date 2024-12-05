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
        cities_response = requests.get('http://api:4000/city')
        cities_data = cities_response.json()
        
        # Get housing data
        housing_response = requests.get('http://api:4000/housing')
        housing_data = housing_response.json()
        
        # Get airport data
        airports_response = requests.get('http://api:4000/airports')
        airports_data = airports_response.json()
        
        # Get hospital data
        hospitals_response = requests.get('http://api:4000/hospitals')
        hospitals_data = hospitals_response.json()
        
        # Find the city_id for the selected city
        city_id = None
        city_data = None
        for city in cities_data:
            if city['name'] == selected_city:
                city_id = city['city_id']
                city_data = city
                break
        
        if not city_id:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        # Process housing data
        locations_data = []
        city_housing = [h for h in housing_data if h['City_ID'] == city_id]
        
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
        
        # Process airport data
        airports_data_processed = []
        city_airports = [a for a in airports_data if a['City_ID'] == city_id]
        base_coords = CITY_COORDINATES.get(selected_city, {'lat': 0, 'lon': 0})
        
        for airport in city_airports:
            airports_data_processed.append({
                'name': airport['Name'],
                'zip': airport['Zip'],
                'lat': base_coords['lat'] + abs((hash(str(airport['Zip'])) % 5) / 1000),
                'lon': base_coords['lon'] + ((hash(str(airport['Name'])) % 7) - 3) / 1000
            })
        
        # Process hospital data
        hospitals_data_processed = []
        city_hospitals = [h for h in hospitals_data if h['City_ID'] == city_id]
        
        for hospital in city_hospitals:
            hospitals_data_processed.append({
                'name': hospital['Name'],
                'zip': hospital.get('Zip', ''),
                'lat': base_coords['lat'] + abs((hash(str(hospital['Name'])) % 6) / 1000),
                'lon': base_coords['lon'] + ((hash(str(hospital.get('Name', ''))) % 5) - 2) / 1000
            })
        
        # Create DataFrames
        df_housing = pd.DataFrame(locations_data)
        df_airports = pd.DataFrame(airports_data_processed)
        df_hospitals = pd.DataFrame(hospitals_data_processed)
        
        # Add tooltips for airports and hospitals
        if not df_airports.empty:
            df_airports['tooltip'] = df_airports['name'].astype(str) + ' (Airport)'
        if not df_hospitals.empty:
            df_hospitals['tooltip'] = df_hospitals['name'].astype(str) + ' (Hospital)'
        
        # Debug logging
        print("Airports Response:", airports_response.text)
        print("Hospitals Response:", hospitals_response.text)
        
        # Get airport data
        airports_response = requests.get('http://api:4000/airports')
        airports_data = airports_response.json()
        
        return df_housing, df_airports, df_hospitals
                
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        logger.error(f"Data fetch error: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Get list of cities and create selector
cities = fetch_cities()
selected_city = st.sidebar.selectbox("Select a City", cities)

# Get the data for selected city
try:
    df_housing, df_airports, df_hospitals = get_location_data(selected_city)
    
    if not df_housing.empty:
        ALL_LAYERS = {
            "Housing Locations": pdk.Layer(
                "ScatterplotLayer",
                data=df_housing,
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius=50,
                pickable=True,
            ),
            "Rent Heatmap": pdk.Layer(
                "HexagonLayer",
                data=df_housing,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=2,
                elevation_range=[0, 500],
                get_elevation="rent",
                pickable=True,
                extruded=True,
            ),
            "Airports": pdk.Layer(
                "ScatterplotLayer",
                data=df_airports,
                get_position=["lon", "lat"],
                get_color=[66, 135, 245, 160],  # Blue color for airports
                get_radius=75,
                pickable=True,
            ),
            "Hospitals": pdk.Layer(
                "ScatterplotLayer",
                data=df_hospitals,
                get_position=["lon", "lat"],
                get_color=[245, 66, 66, 160],  # Red color for hospitals
                get_radius=75,
                pickable=True,
            )
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
                        "latitude": df_housing['lat'].mean(),
                        "longitude": df_housing['lon'].mean(),
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
                df_housing[['city', 'zipcode', 'address', 'rent', 'sqft']],
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