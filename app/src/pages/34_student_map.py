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
            st.warning(f"No data found for city: {selected_city}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        # Process housing data
        locations_data = []
        city_housing = [h for h in housing_data if h['City_ID'] == city_id]
        
        base_coords = CITY_COORDINATES.get(selected_city)
        if not base_coords:
            st.error(f"No coordinates found for city: {selected_city}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
        for house in city_housing:
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
        # Create layers for the map with adjusted parameters
        ALL_LAYERS = {
            "Housing Locations": pdk.Layer(
                "ScatterplotLayer",
                data=df_housing,
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius=50,
                pickable=False  # Disabled hover interaction
            ),
            "Rent Heatmap": pdk.Layer(
                "HexagonLayer",
                data=df_housing,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=2,
                elevation_range=[0, 500],
                get_elevation="rent",
                extruded=True,
                pickable=False  # Disabled hover interaction
            ),
            "Airports": pdk.Layer(
                "ScatterplotLayer",
                data=df_airports,
                get_position=["lon", "lat"],
                get_color=[0, 255, 0, 200],
                get_radius=100,
                pickable=False  # Disabled hover interaction
            ),
            "Hospitals": pdk.Layer(
                "ScatterplotLayer",
                data=df_hospitals,
                get_position=["lon", "lat"],
                get_color=[255, 0, 0, 200],
                get_radius=100,
                pickable=False  # Disabled hover interaction
            )
        }

        # Create layer selector and legend in sidebar
        st.sidebar.markdown("### Map Layers")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)
        ]

        # Add legend to sidebar
        st.sidebar.markdown("### Map Legend")
        st.sidebar.markdown("""
        🔴 **Housing Locations** - Small red circles
        📊 **Rent Heatmap** - Colored hexagons (higher = more expensive)
        🟢 **Airports** - Large green circles
        🔴 **Hospitals** - Large red circles
        """)

        # Create the map without tooltip configuration
        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state={
                    "latitude": df_housing['lat'].mean(),
                    "longitude": df_housing['lon'].mean(),
                    "zoom": 12,
                    "pitch": 50,
                },
                layers=selected_layers
            )
        )

        # Add filters and data tables below the map
        st.markdown("### Location Details")

        # Create columns for filters
        col1, col2 = st.columns(2)

        with col1:
            # Category filter
            category = st.selectbox(
                "Filter by category:",
                ["Housing", "Airports", "Hospitals"]
            )

        with col2:
            # Dynamic filter based on category
            if category == "Housing":
                filter_option = st.selectbox(
                    "Filter housing by:",
                    ["Zipcode", "Rent Range", "Square Footage"]
                )
                if filter_option == "Zipcode":
                    filter_value = st.text_input("Enter zipcode:")
                    filtered_df = df_housing[df_housing['zipcode'].astype(str).str.contains(filter_value, case=False, na=False)]
                elif filter_option == "Rent Range":
                    min_rent = st.number_input("Minimum rent:", min_value=0)
                    max_rent = st.number_input("Maximum rent:", min_value=0)
                    filtered_df = df_housing[(df_housing['rent'] >= min_rent) & (df_housing['rent'] <= max_rent)]
                else:  # Square Footage
                    min_sqft = st.number_input("Minimum square feet:", min_value=0)
                    max_sqft = st.number_input("Maximum square feet:", min_value=0)
                    filtered_df = df_housing[(df_housing['sqft'] >= min_sqft) & (df_housing['sqft'] <= max_sqft)]
                
                st.dataframe(filtered_df[['address', 'zipcode', 'rent', 'sqft']])

            elif category == "Airports":
                search_term = st.text_input("Search airports by name:")
                filtered_df = df_airports[df_airports['name'].str.contains(search_term, case=False, na=False)]
                st.dataframe(filtered_df[['name', 'lat', 'lon']])

            else:  # Hospitals
                search_term = st.text_input("Search hospitals by name:")
                filtered_df = df_hospitals[df_hospitals['name'].str.contains(search_term, case=False, na=False)]
                st.dataframe(filtered_df[['name', 'lat', 'lon']])
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