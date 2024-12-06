import streamlit as st
import requests
import json
import os

def display_city_card(city_data):
    with st.container():
        st.subheader(f"📍 {city_data['name']}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Basic Information")
            st.write(f"Cost of Living: ${city_data['cost_of_living']:,.2f}")
            st.write(f"Average Rent: ${city_data['avg_rent']:,.2f}")
            st.write(f"Average Wage: ${city_data['avg_wage']:,.2f}")
        
        with col2:
            metrics = city_data['cost_metrics']
            st.write("Cost Metrics")
            st.write(f"Cost to Wage: {metrics['cost_to_wage_ratio']*100:.1f}%")
            st.write(f"Rent to Wage: {metrics['rent_to_wage_ratio']*100:.1f}%")
            
            national_comp = metrics['cost_vs_national_avg']
            st.write("vs National Average:")
            st.write(f"CoL: {float(national_comp['cost_of_living_percent']):+.1f}%")
            st.write(f"Rent: {float(national_comp['rent_percent']):+.1f}%")
            st.write(f"Wage: {float(national_comp['wage_percent']):+.1f}%")
        st.divider()

def display_cost_analysis():
    st.title("Cost of Living Analysis")
    
    target_cost = st.number_input(
        "Enter target monthly cost of living ($):",
        min_value=0,
        value=2000,
        step=100
    )
    
    if st.button("Analyze"):
        try:
            api_url = f"http://api:4000/city/1/{target_cost}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError as je:
                    st.error("Invalid JSON response from API")
                    st.write("Debug: Raw response:")
                    st.write(response.text)
                    return
                
                # Convert single city response to list
                cities_data = [data] if isinstance(data, dict) else data
                
                if not isinstance(cities_data, list):
                    st.error("Received invalid data structure from API")
                    st.write("Debug: Response data structure:")
                    st.write(data)
                    return
                
                st.subheader(f"Found {len(cities_data)} cities closest to ${target_cost:,}")
                
                for city_data in cities_data:
                    if not isinstance(city_data, dict):
                        st.error(f"Invalid city data format: {city_data}")
                        continue
                    try:
                        display_city_card(city_data)
                    except KeyError as ke:
                        st.error(f"Missing required field in city data: {ke}")
                        st.write("City data structure:", city_data)
        
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            st.write("Debug info:")
            st.write(f"Target URL: {api_url}")

if __name__ == "__main__":
    display_cost_analysis()