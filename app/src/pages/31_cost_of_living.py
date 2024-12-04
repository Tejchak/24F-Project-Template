import streamlit as st
import requests
import json

def display_cost_analysis():
    st.title("Cost of Living Analysis")
    
    # Input field for cost of living
    target_cost = st.number_input(
        "Enter target monthly cost of living ($):",
        min_value=0,
        value=2000,
        step=100
    )
    
    if st.button("Analyze"):
        try:
            api_url = f"http://api:4000/city/1/{target_cost}"
            st.write(f"Attempting to connect to: {api_url}")
            
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Create two columns for layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Basic Information")
                    st.write(f"City: {data['name']}")
                    st.write(f"Cost of Living: ${data['cost_of_living']:,.2f}")
                    st.write(f"Average Rent: ${data['avg_rent']:,.2f}")
                    st.write(f"Average Wage: ${data['avg_wage']:,.2f}")
                
                with col2:
                    st.subheader("Cost Metrics")
                    metrics = data['cost_metrics']
                    
                    st.write("Cost Ratios:")
                    st.write(f"- Cost to Wage: {metrics['cost_to_wage_ratio']:.2f}")
                    st.write(f"- Rent to Wage: {metrics['rent_to_wage_ratio']:.2f}")
                    
                    st.write("\nComparison to National Average:")
                    national_comp = metrics['cost_vs_national_avg']
                    st.write(f"- Cost of Living: {national_comp['cost_of_living_percent']:+.1f}%")
                    st.write(f"- Rent: {national_comp['rent_percent']:+.1f}%")
                    st.write(f"- Wage: {national_comp['wage_percent']:+.1f}%")
                
            else:
                st.error("No cities found matching the specified cost of living.")
                
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            st.write("Debug info:")
            st.write(f"Target URL: {api_url}")

if __name__ == "__main__":
    display_cost_analysis()
