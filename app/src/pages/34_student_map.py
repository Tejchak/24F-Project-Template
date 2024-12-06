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
        # Create layers for the map with adjusted parameters
        ALL_LAYERS = {
            "Housing Locations": pdk.Layer(
                "ScatterplotLayer",
                data=df_housing,
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius=50,
                pickable=True,
                auto_highlight=True,
                get_tooltip="Housing Location"
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
                pickable=True,
                auto_highlight=True,
                get_tooltip="Rent Heatmap Area"
            ),
            "Airports": pdk.Layer(
                "ScatterplotLayer",
                data=df_airports,
                get_position=["lon", "lat"],
                get_color=[0, 255, 0, 200],
                get_radius=100,
                pickable=True,
                auto_highlight=True,
                get_tooltip="✈️ Airport"
            ),
            "Hospitals": pdk.Layer(
                "ScatterplotLayer",
                data=df_hospitals,
                get_position=["lon", "lat"],
                get_color=[255, 0, 0, 200],
                get_radius=100,
                pickable=True,
                auto_highlight=True,
                get_tooltip="🏥 Hospital"
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
        legend_html = """
            <style>
                .legend-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                }
                .legend-icon {
                    width: 15px;
                    height: 15px;
                    border-radius: 50%;
                    margin-right: 10px;
                }
                .legend-text {
                    display: flex;
                    flex-direction: column;
                }
                .legend-title {
                    font-weight: bold;
                    margin-bottom: 2px;
                }
                .legend-description {
                    font-size: 0.85em;
                    color: #666;
                }
                .heatmap-icon {
                    background: linear-gradient(to right, #ff4b1f, #ff9068);
                    border-radius: 3px;
                }
                .heatmap-details {
                    margin-top: 5px;
                    font-size: 0.8em;
                    color: #666;
                    padding-left: 5px;
                    border-left: 2px solid #ff9068;
                }
            </style>
            
            <div class="legend-item">
                <div class="legend-icon" style="background-color: rgba(200, 30, 0, 0.6);"></div>
                <div class="legend-text">
                    <div class="legend-title">Housing Locations</div>
                    <div class="legend-description">Individual housing properties</div>
                </div>
            </div>
            
            <div class="legend-item">
                <div class="legend-icon heatmap-icon"></div>
                <div class="legend-text">
                    <div class="legend-title">Rent Heatmap</div>
                    <div class="legend-description">3D visualization of rental prices</div>
                    <div class="heatmap-details">
                        • Taller hexagons = Higher rent<br>
                        • Darker colors = More properties<br>
                        • Clusters show rental hotspots
                    </div>
                </div>
            </div>
            
            <div class="legend-item">
                <div class="legend-icon" style="background-color: rgba(0, 255, 0, 0.8);"></div>
                <div class="legend-text">
                    <div class="legend-title">Airports ✈️</div>
                    <div class="legend-description">Major airports in the area</div>
                </div>
            </div>
            
            <div class="legend-item">
                <div class="legend-icon" style="background-color: rgba(255, 0, 0, 0.8);"></div>
                <div class="legend-text">
                    <div class="legend-title">Hospitals 🏥</div>
                    <div class="legend-description">Medical facilities</div>
                </div>
            </div>
        """
        st.sidebar.markdown(legend_html, unsafe_allow_html=True)
        
        # Add back button to sidebar
        st.sidebar.markdown("---")  # Add a divider
        if st.sidebar.button("← Back to Student Home", use_container_width=True):
            st.switch_page("pages/29_Student_Home.py")

        # Create the map
        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state={
                    "latitude": df_housing['lat'].mean(),
                    "longitude": df_housing['lon'].mean(),
                    "zoom": 12,
                    "pitch": 50,
                },
                layers=selected_layers,
                tooltip={"text": "🏥 Hospital"} if "Hospitals" in df_hospitals else None or
                {"text": "✈️ Airport"} if "Airports" in selected_layers else None or
                {"text": "📊 Rent Heatmap"} if "Rent Heatmap" in selected_layers else None or
                {"text": "🔴 Housing Locations"} if "Housing Locations" in selected_layers else None
            )
        )
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

# Add this after the map visualization

# Location Details header
st.markdown("""
    <h2 style='color: #4285F4;'>Location Details</h2>
""", unsafe_allow_html=True)

# Category selector
st.markdown("#### 🔍 Select Category to Filter:")
category = st.selectbox(
    "Category",
    ["🏠 Housing", "✈️ Airports", "🏥 Hospitals"],
    key="category_filter",
    label_visibility="collapsed"
)

# Create columns for filters and metrics
col_filters, col_metrics = st.columns([2, 1])

with col_filters:
    if "🏠 Housing" in category:
        st.markdown("#### 🎯 Filter Housing By:")
        filter_type = st.selectbox(
            "Filter Type",
            ["📋 All", "📍 Zipcode", "💰 Price Range", "📐 Square Footage"],
            key="housing_filter",
            label_visibility="collapsed"
        )

        # Filter inputs based on type
        if "📍 Zipcode" in filter_type:
            zipcode = st.text_input("Enter zipcode:", placeholder="e.g., 02115")
            if zipcode:
                filtered_df = df_housing[df_housing['city'] == selected_city] if not df_housing.empty else pd.DataFrame()
                filtered_df = filtered_df[filtered_df['zipcode'].astype(str).str.contains(zipcode)]
        
        elif "💰 Price Range" in filter_type:
            col3, col4 = st.columns(2)
            with col3:
                min_rent = st.number_input("Min rent ($):", min_value=0, step=100)
            with col4:
                max_rent = st.number_input("Max rent ($):", min_value=0, step=100)
            
            if min_rent > 0 or max_rent > 0:
                filtered_df = df_housing[df_housing['city'] == selected_city] if not df_housing.empty else pd.DataFrame()
                filtered_df = filtered_df[
                    (filtered_df['rent'] >= min_rent) & 
                    (filtered_df['rent'] <= max_rent if max_rent > 0 else True)
                ]
        
        elif "📐 Square Footage" in filter_type:
            col3, col4 = st.columns(2)
            with col3:
                min_sqft = st.number_input("Min sq ft:", min_value=0, step=100)
            with col4:
                max_sqft = st.number_input("Max sq ft:", min_value=0, step=100)
            
            if min_sqft > 0 or max_sqft > 0:
                filtered_df = df_housing[df_housing['city'] == selected_city] if not df_housing.empty else pd.DataFrame()
                filtered_df = filtered_df[
                    (filtered_df['sqft'] >= min_sqft) & 
                    (filtered_df['sqft'] <= max_sqft if max_sqft > 0 else True)
                ]
        else:  # All
            filtered_df = df_housing[df_housing['city'] == selected_city] if not df_housing.empty else pd.DataFrame()

with col_metrics:
    if not filtered_df.empty:
        st.markdown("""
            <style>
            .metric-container {
                padding: 10px;
                width: 100%;
            }
            .metric-card {
                background-color: white;
                padding: 15px 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 15px;
                width: 100%;
            }
            .metric-title {
                color: #666;
                font-size: 1.1em;
                margin-bottom: 5px;
                font-weight: 500;
            }
            .metric-value {
                color: #4285F4;
                font-size: 2.5em;
                font-weight: bold;
                margin: 0;
                line-height: 1.1;
            }
            .metrics-column {
                display: flex;
                flex-direction: column;
                width: 250px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Calculate metrics
        avg_rent = f"${filtered_df['rent'].mean():,.0f}"
        avg_sqft = f"{filtered_df['sqft'].mean():,.0f}"
        loc_count = str(len(filtered_df))
        
        metrics_html = f"""
        <div class="metrics-column">
            <div class='metric-card'>
                <div class='metric-title'>Average Rent</div>
                <div class='metric-value'>{avg_rent}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-title'>Average Sq Ft</div>
                <div class='metric-value'>{avg_sqft}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-title'>Locations Found</div>
                <div class='metric-value'>{loc_count}</div>
            </div>
        </div>
        """
        
        st.markdown(metrics_html, unsafe_allow_html=True)

# Search Results (outside the columns, full width)
if "🏠 Housing" in category and not filtered_df.empty:
    st.markdown("#### Search Results")
    st.dataframe(
        filtered_df[['address', 'zipcode', 'rent', 'sqft']],
        column_config={
            'address': st.column_config.TextColumn('📍 Address'),
            'zipcode': st.column_config.TextColumn('🏘️ Zipcode'),
            'rent': st.column_config.NumberColumn('💰 Rent', format="$%d"),
            'sqft': st.column_config.NumberColumn('📐 Square Feet', format="%d sq ft")
        },
        hide_index=True,
        use_container_width=True
    )

    # Add detailed view option
    if st.checkbox("Show Detailed View", key="detailed_view"):
        st.markdown("#### 📋 Detailed Property Information")
        for _, row in filtered_df.iterrows():
            with st.expander(f"📍 {row['address']} - ${row['rent']:,}/month"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        * **🏘️ Zipcode:** {row['zipcode']}
                        * **💰 Monthly Rent:** ${row['rent']:,}
                    """)
                with col2:
                    st.markdown(f"""
                        * **📐 Square Feet:** {row['sqft']:,}
                        * **💵 Price per Sq Ft:** ${row['rent']/row['sqft']:.2f}/sq ft
                    """)
                
                # Add a divider between properties
                st.markdown("---")

elif "✈️ Airports" in category and not df_airports.empty:
    st.markdown("#### Search Results")
    search_term = st.text_input("🔍 Search by name:", placeholder="Enter airport name...")
    filtered_airports = df_airports if not search_term else df_airports[
        df_airports['name'].str.contains(search_term, case=False, na=False)
    ]
    st.dataframe(
        filtered_airports[['name', 'zip']],
        column_config={
            'name': st.column_config.TextColumn('✈️ Airport Name'),
            'zip': st.column_config.TextColumn('📍 Zip Code')
        },
        hide_index=True,
        use_container_width=True
    )

elif "🏥 Hospitals" in category and not df_hospitals.empty:
    st.markdown("#### Search Results")
    search_term = st.text_input("🔍 Search by name:", placeholder="Enter hospital name...")
    filtered_hospitals = df_hospitals if not search_term else df_hospitals[
        df_hospitals['name'].str.contains(search_term, case=False, na=False)
    ]
    st.dataframe(
        filtered_hospitals[['name', 'zip']],
        column_config={
            'name': st.column_config.TextColumn('🏥 Hospital Name'),
            'zip': st.column_config.TextColumn('📍 Zip Code')
        },
        hide_index=True,
        use_container_width=True
    )

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)